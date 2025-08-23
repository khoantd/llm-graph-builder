import os
import json
import time
import logging

import threading
from datetime import datetime
from typing import Any
from dotenv import load_dotenv

from langchain_neo4j import Neo4jVector
from langchain_neo4j import Neo4jChatMessageHistory
from langchain_neo4j import GraphCypherQAChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain.retrievers.document_compressors import EmbeddingsFilter, DocumentCompressorPipeline
from langchain_text_splitters import TokenTextSplitter
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory 
from langchain_core.callbacks import StdOutCallbackHandler, BaseCallbackHandler

# LangChain chat models
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_fireworks import ChatFireworks
from langchain_aws import ChatBedrock
from langchain_community.chat_models import ChatOllama

# Local imports
from src.llm import get_llm
from src.shared.common_fn import load_embedding_model
from src.shared.constants import *
from src.environment_config import get_env_var, env_config

# Load environment configuration
env_config.log_configuration_summary()

EMBEDDING_MODEL = get_env_var('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
EMBEDDING_FUNCTION , _ = load_embedding_model(EMBEDDING_MODEL) 

class SessionChatHistory:
    history_dict = {}

    @classmethod
    def get_chat_history(cls, session_id):
        """Retrieve or create chat message history for a given session ID."""
        try:
            if session_id not in cls.history_dict:
                logging.info(f"Creating new ChatMessageHistory Local for session ID: {session_id}")
                cls.history_dict[session_id] = ChatMessageHistory()
            else:
                logging.info(f"Retrieved existing ChatMessageHistory Local for session ID: {session_id}")
                # Validate existing history
                try:
                    # Test if the history can be accessed without errors
                    test_messages = cls.history_dict[session_id].messages
                    logging.info(f"Successfully validated history for session {session_id}")
                except Exception as e:
                    logging.warning(f"Corrupted history detected for session {session_id}, creating fresh history: {e}")
                    cls.history_dict[session_id] = ChatMessageHistory()
            
            return cls.history_dict[session_id]
        except Exception as e:
            logging.error(f"Error in get_chat_history for session {session_id}: {e}")
            # Return a fresh history if there's any error
            cls.history_dict[session_id] = ChatMessageHistory()
            return cls.history_dict[session_id]

class CustomCallback(BaseCallbackHandler):

    def __init__(self):
        self.transformed_question = None
    
    def on_llm_end(
        self,response, **kwargs: Any
    ) -> None:
        logging.info("question transformed")
        self.transformed_question = response.generations[0][0].text.strip()

def get_history_by_session_id(session_id):
    try:
        return SessionChatHistory.get_chat_history(session_id)
    except Exception as e:
        logging.error(f"Failed to get history for session ID '{session_id}': {e}")
        raise

def get_total_tokens(ai_response, llm):
    try:
        if isinstance(llm, (ChatOpenAI, AzureChatOpenAI, ChatFireworks, ChatGroq)):
            total_tokens = ai_response.response_metadata.get('token_usage', {}).get('total_tokens', 0)
        
        elif isinstance(llm, ChatVertexAI):
            total_tokens = ai_response.response_metadata.get('usage_metadata', {}).get('prompt_token_count', 0)
        
        elif isinstance(llm, ChatBedrock):
            total_tokens = ai_response.response_metadata.get('usage', {}).get('total_tokens', 0)
        
        elif isinstance(llm, ChatAnthropic):
            input_tokens = int(ai_response.response_metadata.get('usage', {}).get('input_tokens', 0))
            output_tokens = int(ai_response.response_metadata.get('usage', {}).get('output_tokens', 0))
            total_tokens = input_tokens + output_tokens
        
        elif isinstance(llm, ChatOllama):
            total_tokens = ai_response.response_metadata.get("prompt_eval_count", 0)
        
        else:
            logging.warning(f"Unrecognized language model: {type(llm)}. Returning 0 tokens.")
            total_tokens = 0

    except Exception as e:
        logging.error(f"Error retrieving total tokens: {e}")
        total_tokens = 0

    return total_tokens

def clear_chat_history(graph, session_id,local=False):
    try:
        if not local:
            # Use the safe wrapper for Neo4jChatMessageHistory
            history = SafeNeo4jChatMessageHistory(
                graph=graph,
                session_id=session_id
            )
        else:
            history = get_history_by_session_id(session_id)
        
        history.clear()

        return {
            "session_id": session_id, 
            "message": "The chat history has been cleared.", 
            "user": "chatbot"
        }
    
    except Exception as e:
        logging.error(f"Error clearing chat history for session {session_id}: {e}")
        return {
            "session_id": session_id, 
            "message": "Failed to clear chat history.", 
            "user": "chatbot"
        }

def get_sources_and_chunks(sources_used, docs):
    chunkdetails_list = []
    sources_used_set = set(sources_used)
    seen_ids_and_scores = set()  

    for doc in docs:
        try:
            source = doc.metadata.get("source")
            chunkdetails = doc.metadata.get("chunkdetails", [])

            if source in sources_used_set:
                for chunkdetail in chunkdetails:
                    id = chunkdetail.get("id")
                    score = round(chunkdetail.get("score", 0), 4)

                    id_and_score = (id, score)

                    if id_and_score not in seen_ids_and_scores:
                        seen_ids_and_scores.add(id_and_score)
                        chunkdetails_list.append({**chunkdetail, "score": score})

        except Exception as e:
            logging.error(f"Error processing document: {e}")

    result = {
        'sources': sources_used,
        'chunkdetails': chunkdetails_list,
    }
    return result

def get_rag_chain(llm, system_template=CHAT_SYSTEM_TEMPLATE):
    try:
        question_answering_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "human",
                    "User question: {input}"
                ),
            ]
        )

        question_answering_chain = question_answering_prompt | llm

        return question_answering_chain

    except Exception as e:
        logging.error(f"Error creating RAG chain: {e}")
        raise

def format_documents(documents, model,chat_mode_settings):
    prompt_token_cutoff = 4
    for model_names, value in CHAT_TOKEN_CUT_OFF.items():
        if model in model_names:
            prompt_token_cutoff = value
            break

    sorted_documents = sorted(documents, key=lambda doc: doc.state.get("query_similarity_score", 0), reverse=True)
    sorted_documents = sorted_documents[:prompt_token_cutoff]

    formatted_docs = list()
    sources = set()
    entities = dict()
    global_communities = list()


    for doc in sorted_documents:
        try:
            source = doc.metadata.get('source', "unknown")
            sources.add(source)
            if 'entities' in doc.metadata:
                if chat_mode_settings["mode"] == CHAT_ENTITY_VECTOR_MODE:
                    entity_ids = [entry['entityids'] for entry in doc.metadata['entities'] if 'entityids' in entry]
                    entities.setdefault('entityids', set()).update(entity_ids)
                else:
                    if 'entityids' in doc.metadata['entities']:
                        entities.setdefault('entityids', set()).update(doc.metadata['entities']['entityids'])
                    if 'relationshipids' in doc.metadata['entities']:
                        entities.setdefault('relationshipids', set()).update(doc.metadata['entities']['relationshipids'])
                
            if 'communitydetails' in doc.metadata:
                existing_ids = {entry['id'] for entry in global_communities}
                new_entries = [entry for entry in doc.metadata["communitydetails"] if entry['id'] not in existing_ids]
                global_communities.extend(new_entries)

            formatted_doc = (
                "Document start\n"
                f"This Document belongs to the source {source}\n"
                f"Content: {doc.page_content}\n"
                "Document end\n"
            )
            formatted_docs.append(formatted_doc)
        
        except Exception as e:
            logging.error(f"Error formatting document: {e}")
    
    return "\n\n".join(formatted_docs), sources,entities,global_communities

def process_documents(docs, question, messages, llm, model,chat_mode_settings):
    start_time = time.time()
    
    try:
        formatted_docs, sources, entitydetails, communities = format_documents(docs, model,chat_mode_settings)
        
        rag_chain = get_rag_chain(llm=llm)
        
        ai_response = rag_chain.invoke({
            "messages": messages[:-1],
            "context": formatted_docs,
            "input": question
        })

        result = {'sources': list(), 'nodedetails': dict(), 'entities': dict()}
        node_details = {"chunkdetails":list(),"entitydetails":list(),"communitydetails":list()}
        entities = {'entityids':list(),"relationshipids":list()}

        if chat_mode_settings["mode"] == CHAT_ENTITY_VECTOR_MODE:
            node_details["entitydetails"] = entitydetails

        elif chat_mode_settings["mode"] == CHAT_GLOBAL_VECTOR_FULLTEXT_MODE:
            node_details["communitydetails"] = communities
        else:
            sources_and_chunks = get_sources_and_chunks(sources, docs)
            result['sources'] = sources_and_chunks['sources']
            node_details["chunkdetails"] = sources_and_chunks["chunkdetails"]
            entities.update(entitydetails)

        result["nodedetails"] = node_details
        result["entities"] = entities

        content = ai_response.content
        total_tokens = get_total_tokens(ai_response, llm)
        
        predict_time = time.time() - start_time
        logging.info(f"Final response predicted in {predict_time:.2f} seconds")

    except Exception as e:
        logging.error(f"Error processing documents: {e}")
        raise
    
    return content, result, total_tokens, formatted_docs

def retrieve_documents(doc_retriever, messages):

    start_time = time.time()
    try:
        handler = CustomCallback()
        docs = doc_retriever.invoke({"messages": messages},{"callbacks":[handler]})
        transformed_question = handler.transformed_question
        if transformed_question:
            logging.info(f"Transformed question : {transformed_question}")
        doc_retrieval_time = time.time() - start_time
        logging.info(f"Documents retrieved in {doc_retrieval_time:.2f} seconds")
        
    except Exception as e:
        error_message = f"Error retrieving documents: {str(e)}"
        logging.error(error_message)
        docs = None
        transformed_question = None

    
    return docs,transformed_question

def create_document_retriever_chain(llm, retriever):
    try:
        logging.info("Starting to create document retriever chain")

        query_transform_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", QUESTION_TRANSFORM_TEMPLATE),
                MessagesPlaceholder(variable_name="messages")
            ]
        )

        output_parser = StrOutputParser()

        splitter = TokenTextSplitter(chunk_size=CHAT_DOC_SPLIT_SIZE, chunk_overlap=0)
        embeddings_filter = EmbeddingsFilter(
            embeddings=EMBEDDING_FUNCTION,
            similarity_threshold=CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD
        )

        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[splitter, embeddings_filter]
        )

        compression_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=retriever
        )

        query_transforming_retriever_chain = RunnableBranch(
            (
                lambda x: len(x.get("messages", [])) == 1,
                (lambda x: x["messages"][-1].content) | compression_retriever,
            ),
            query_transform_prompt | llm | output_parser | compression_retriever,
        ).with_config(run_name="chat_retriever_chain")

        logging.info("Successfully created document retriever chain")
        return query_transforming_retriever_chain

    except Exception as e:
        logging.error(f"Error creating document retriever chain: {e}", exc_info=True)
        raise

def initialize_neo4j_vector(graph, chat_mode_settings):
    try:
        retrieval_query = chat_mode_settings.get("retrieval_query")
        index_name = chat_mode_settings.get("index_name")
        keyword_index = chat_mode_settings.get("keyword_index", "")
        node_label = chat_mode_settings.get("node_label")
        embedding_node_property = chat_mode_settings.get("embedding_node_property")
        text_node_properties = chat_mode_settings.get("text_node_properties")


        if not retrieval_query or not index_name:
            raise ValueError("Required settings 'retrieval_query' or 'index_name' are missing.")

        if keyword_index:
            neo_db = Neo4jVector.from_existing_graph(
                embedding=EMBEDDING_FUNCTION,
                index_name=index_name,
                retrieval_query=retrieval_query,
                graph=graph,
                search_type="hybrid",
                node_label=node_label,
                embedding_node_property=embedding_node_property,
                text_node_properties=text_node_properties,
                keyword_index_name=keyword_index
            )
            logging.info(f"Successfully retrieved Neo4jVector Fulltext index '{index_name}' and keyword index '{keyword_index}'")
        else:
            neo_db = Neo4jVector.from_existing_graph(
                embedding=EMBEDDING_FUNCTION,
                index_name=index_name,
                retrieval_query=retrieval_query,
                graph=graph,
                node_label=node_label,
                embedding_node_property=embedding_node_property,
                text_node_properties=text_node_properties
            )
            logging.info(f"Successfully retrieved Neo4jVector index '{index_name}'")
    except Exception as e:
        index_name = chat_mode_settings.get("index_name")
        logging.error(f"Error retrieving Neo4jVector index {index_name} : {e}")
        raise
    return neo_db

def create_retriever(neo_db, document_names, chat_mode_settings,search_k, score_threshold,ef_ratio):
    if document_names and chat_mode_settings["document_filter"]:
        retriever = neo_db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                'top_k': search_k,
                'effective_search_ratio': ef_ratio,
                'score_threshold': score_threshold,
                'filter': {'fileName': {'$in': document_names}}
            }
        )
        logging.info(f"Successfully created retriever with search_k={search_k}, score_threshold={score_threshold} for documents {document_names}")
    else:
        retriever = neo_db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={'top_k': search_k,'effective_search_ratio': ef_ratio, 'score_threshold': score_threshold}
        )
        logging.info(f"Successfully created retriever with search_k={search_k}, score_threshold={score_threshold}")
    return retriever

def get_neo4j_retriever(graph, document_names,chat_mode_settings, score_threshold=CHAT_SEARCH_KWARG_SCORE_THRESHOLD):
    try:

        neo_db = initialize_neo4j_vector(graph, chat_mode_settings)
        # document_names= list(map(str.strip, json.loads(document_names)))
        search_k = chat_mode_settings["top_k"]
        ef_ratio = int(os.getenv("EFFECTIVE_SEARCH_RATIO", "2")) if os.getenv("EFFECTIVE_SEARCH_RATIO", "2").isdigit() else 2
        retriever = create_retriever(neo_db, document_names,chat_mode_settings, search_k, score_threshold,ef_ratio)
        return retriever
    except Exception as e:
        index_name = chat_mode_settings.get("index_name")
        logging.error(f"Error retrieving Neo4jVector index  {index_name} or creating retriever: {e}")
        raise Exception(f"An error occurred while retrieving the Neo4jVector index or creating the retriever. Please drop and create a new vector index '{index_name}': {e}") from e 


def setup_chat(model, graph, document_names, chat_mode_settings):
    start_time = time.time()
    try:
        if model == "diffbot":
            model = get_env_var('DEFAULT_DIFFBOT_CHAT_MODEL', 'openai_gpt_4o')
        
        llm, model_name = get_llm(model=model)
        logging.info(f"Model called in chat: {model} (version: {model_name})")

        retriever = get_neo4j_retriever(graph=graph, chat_mode_settings=chat_mode_settings, document_names=document_names)
        doc_retriever = create_document_retriever_chain(llm, retriever)
        
        chat_setup_time = time.time() - start_time
        logging.info(f"Chat setup completed in {chat_setup_time:.2f} seconds")
        
    except Exception as e:
        logging.error(f"Error during chat setup: {e}", exc_info=True)
        raise
    
    return llm, doc_retriever, model_name

def process_chat_response(messages, history, question, model, graph, document_names, chat_mode_settings):
    try:
        llm, doc_retriever, model_version = setup_chat(model, graph, document_names, chat_mode_settings)
        
        docs,transformed_question = retrieve_documents(doc_retriever, messages)  

        if docs:
            content, result, total_tokens,formatted_docs = process_documents(docs, question, messages, llm, model, chat_mode_settings)
        else:
            content = "I couldn't find any relevant documents to answer your question."
            result = {"sources": list(), "nodedetails": list(), "entities": list()}
            total_tokens = 0
            formatted_docs = ""
        
        ai_response = AIMessage(content=content)
        messages.append(ai_response)

        summarization_thread = threading.Thread(target=summarize_and_log, args=(history, messages, llm))
        summarization_thread.start()
        logging.info("Summarization thread started.")
        # summarize_and_log(history, messages, llm)
        metric_details = {"question":question,"contexts":formatted_docs,"answer":content}
        return {
            "session_id": "",  
            "message": content,
            "info": {
                # "metrics" : metrics,
                "sources": result["sources"],
                "model": model_version,
                "nodedetails": result["nodedetails"],
                "total_tokens": total_tokens,
                "response_time": 0,
                "mode": chat_mode_settings["mode"],
                "entities": result["entities"],
                "metric_details": metric_details,
            },
            
            "user": "chatbot"
        }
    
    except Exception as e:
        logging.exception(f"Error processing chat response at {datetime.now()}: {str(e)}")
        return {
            "session_id": "",
            "message": "Something went wrong",
            "info": {
                "metrics" : [],
                "sources": [],
                "nodedetails": [],
                "total_tokens": 0,
                "response_time": 0,
                "error": f"{type(e).__name__}: {str(e)}",
                "mode": chat_mode_settings["mode"],
                "entities": [],
                "metric_details": {},
            },
            "user": "chatbot"
        }

def summarize_and_log(history, stored_messages, llm):
    logging.info("Starting summarization in a separate thread.")
    if not stored_messages:
        logging.info("No messages to summarize.")
        return False

    try:
        start_time = time.time()

        summarization_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "human",
                    "Summarize the above chat messages into a concise message, focusing on key points and relevant details that could be useful for future conversations. Exclude all introductions and extraneous information."
                ),
            ]
        )
        summarization_chain = summarization_prompt | llm

        summary_message = summarization_chain.invoke({"chat_history": stored_messages})

        with threading.Lock():
            history.clear()
            history.add_user_message("Our current conversation summary till now")
            history.add_message(summary_message)

        history_summarized_time = time.time() - start_time
        logging.info(f"Chat History summarized in {history_summarized_time:.2f} seconds")

        return True

    except Exception as e:
        logging.error(f"An error occurred while summarizing messages: {e}", exc_info=True)
        return False 
    
def create_graph_chain(model, graph):
    try:
        logging.info(f"Graph QA Chain using LLM model: {model}")

        cypher_llm,model_name = get_llm(model)
        qa_llm,model_name = get_llm(model)
        graph_chain = GraphCypherQAChain.from_llm(
            cypher_llm=cypher_llm,
            qa_llm=qa_llm,
            validate_cypher= True,
            graph=graph,
            # verbose=True, 
            allow_dangerous_requests=True,
            return_intermediate_steps = True,
            top_k=3
        )

        logging.info("GraphCypherQAChain instance created successfully.")
        return graph_chain,qa_llm,model_name

    except Exception as e:
        logging.error(f"An error occurred while creating the GraphCypherQAChain instance. : {e}") 

def get_graph_response(graph_chain, question):
    try:
        cypher_res = graph_chain.invoke({"query": question})
        
        response = cypher_res.get("result")
        cypher_query = ""
        context = []

        for step in cypher_res.get("intermediate_steps", []):
            if "query" in step:
                cypher_string = step["query"]
                cypher_query = cypher_string.replace("cypher\n", "").replace("\n", " ").strip() 
            elif "context" in step:
                context = step["context"]
        return {
            "response": response,
            "cypher_query": cypher_query,
            "context": context
        }
    
    except Exception as e:
        logging.error(f"An error occurred while getting the graph response : {e}")

def process_graph_response(model, graph, question, messages, history):
    try:
        graph_chain, qa_llm, model_version = create_graph_chain(model, graph)
        
        graph_response = get_graph_response(graph_chain, question)
        
        ai_response_content = graph_response.get("response", "Something went wrong")
        ai_response = AIMessage(content=ai_response_content)
        
        messages.append(ai_response)
        # summarize_and_log(history, messages, qa_llm)
        summarization_thread = threading.Thread(target=summarize_and_log, args=(history, messages, qa_llm))
        summarization_thread.start()
        logging.info("Summarization thread started.")
        metric_details = {"question":question,"contexts":graph_response.get("context", ""),"answer":ai_response_content}
        result = {
            "session_id": "", 
            "message": ai_response_content,
            "info": {
                "model": model_version,
                "cypher_query": graph_response.get("cypher_query", ""),
                "context": graph_response.get("context", ""),
                "mode": "graph",
                "response_time": 0,
                "metric_details": metric_details,
            },
            "user": "chatbot"
        }
        
        return result
    
    except Exception as e:
        logging.exception(f"Error processing graph response at {datetime.now()}: {str(e)}")
        return {
            "session_id": "",  
            "message": "Something went wrong",
            "info": {
                "model": model_version,
                "cypher_query": "",
                "context": "",
                "mode": "graph",
                "response_time": 0,
                "error": f"{type(e).__name__}: {str(e)}"
            },
            "user": "chatbot"
        }

class SafeNeo4jChatMessageHistory:
    """
    A wrapper around Neo4jChatMessageHistory that safely handles message retrieval
    and prevents 'Got unexpected message type: None' errors.
    """
    
    def __init__(self, graph, session_id):
        self.neo4j_history = Neo4jChatMessageHistory(graph=graph, session_id=session_id)
        self._session_id = session_id  # Store session_id explicitly
        self._cached_messages = None
        self._messages_validated = False
    
    @property
    def session_id(self):
        """Return the session ID."""
        return self._session_id
    
    def _validate_and_cache_messages(self):
        """Validate and cache messages to avoid repeated validation errors."""
        if self._messages_validated:
            return self._cached_messages
            
        try:
            # Try to get messages from the underlying Neo4jChatMessageHistory
            raw_messages = self.neo4j_history._messages if hasattr(self.neo4j_history, '_messages') else []
            valid_messages = []
            
            for message in raw_messages:
                if message and hasattr(message, 'type') and message.type is not None:
                    valid_messages.append(message)
                else:
                    logging.warning(f"Skipping invalid message in session {self._session_id}: {message}")
            
            self._cached_messages = valid_messages
            self._messages_validated = True
            logging.info(f"Successfully validated {len(valid_messages)} messages for session {self._session_id}")
            return valid_messages
            
        except Exception as e:
            logging.error(f"Error validating messages for session {self._session_id}: {e}")
            self._cached_messages = []
            self._messages_validated = True
            return []
    
    @property
    def messages(self):
        """Safely return validated messages."""
        return self._validate_and_cache_messages()
    
    def add_message(self, message):
        """Add a message to the history."""
        try:
            self.neo4j_history.add_message(message)
            # Invalidate cache to force re-validation
            self._messages_validated = False
            self._cached_messages = None
        except Exception as e:
            logging.error(f"Error adding message to history: {e}")
    
    def clear(self):
        """Clear the chat history."""
        try:
            self.neo4j_history.clear()
            self._cached_messages = []
            self._messages_validated = True
        except Exception as e:
            logging.error(f"Error clearing history: {e}")

def create_neo4j_chat_message_history(graph, session_id, write_access=True):
    """
    Creates and returns a safe chat message history instance.

    """
    try:
        if write_access: 
            # Use the safe wrapper for Neo4jChatMessageHistory
            history = SafeNeo4jChatMessageHistory(
                graph=graph,
                session_id=session_id
            )
            return history
        
        history = get_history_by_session_id(session_id)
        return history

    except Exception as e:
        logging.error(f"Error creating chat message history: {e}")
        # Return a fresh history object if there's an error
        return ChatMessageHistory()

def get_chat_mode_settings(mode,settings_map=CHAT_MODE_CONFIG_MAP):
    default_settings = settings_map[CHAT_DEFAULT_MODE]
    try:
        chat_mode_settings = settings_map.get(mode, default_settings)
        chat_mode_settings["mode"] = mode
        
        logging.info(f"Chat mode settings: {chat_mode_settings}")
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        raise

    return chat_mode_settings
    
def validate_and_clean_messages(history):
    """
    Validates and cleans chat messages to remove invalid entries.
    
    Args:
        history: ChatMessageHistory object
        
    Returns:
        list: Cleaned list of valid messages
    """
    try:
        # For Neo4jChatMessageHistory, we need to handle the messages access more carefully
        if hasattr(history, '_messages'):
            # Access the raw messages directly to avoid LangChain validation
            raw_messages = history._messages
            valid_messages = []
            
            for message in raw_messages:
                # Check if message has required attributes and is not None
                if message and hasattr(message, 'type') and message.type is not None:
                    valid_messages.append(message)
                else:
                    logging.warning(f"Skipping invalid message: {message}")
                    
            return valid_messages
        else:
            # For regular ChatMessageHistory, use the normal messages property
            messages = history.messages
            valid_messages = []
            
            for message in messages:
                if hasattr(message, 'type') and message.type is not None:
                    valid_messages.append(message)
                else:
                    logging.warning(f"Skipping invalid message: {message}")
                    
            return valid_messages
    except Exception as e:
        logging.error(f"Error validating messages: {e}")
        # Return empty list if validation fails
        return []

def safe_get_messages(history):
    """
    Safely retrieves messages from chat history, handling various error cases.
    
    Args:
        history: ChatMessageHistory or Neo4jChatMessageHistory object
        
    Returns:
        list: List of valid messages or empty list if error occurs
    """
    try:
        # Try to get messages using the validate_and_clean_messages function
        return validate_and_clean_messages(history)
    except Exception as e:
        logging.error(f"Error in safe_get_messages: {e}")
        # If all else fails, return empty list
        return []

def QA_RAG(graph,model, question, document_names, session_id, mode, write_access=True):
    logging.info(f"Chat Mode: {mode}")

    history = create_neo4j_chat_message_history(graph, session_id, write_access)
    
    # Get messages safely - the SafeNeo4jChatMessageHistory wrapper handles validation
    try:
        messages = history.messages
        logging.info(f"Successfully retrieved {len(messages)} messages from history")
    except Exception as e:
        logging.error(f"Error accessing chat history messages: {e}")
        # Create fresh history if there's an error
        history = ChatMessageHistory()
        messages = []

    user_question = HumanMessage(content=question)
    messages.append(user_question)

    if mode == CHAT_GRAPH_MODE:
        result = process_graph_response(model, graph, question, messages, history)
    else:
        chat_mode_settings = get_chat_mode_settings(mode=mode)
        
        # Safely parse document_names with proper validation
        try:
            if document_names is None:
                document_names = "[]"
            elif isinstance(document_names, str):
                if not document_names.strip():
                    document_names = "[]"
            else:
                document_names = "[]"
                
            parsed_document_names = list(map(str.strip, json.loads(document_names)))
            logging.info(f"Parsed document_names: {parsed_document_names}")
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logging.warning(f"Error parsing document_names '{document_names}': {e}. Using empty list.")
            parsed_document_names = []
        
        if parsed_document_names and not chat_mode_settings["document_filter"]:
            result =  {
                "session_id": "",  
                "message": "Please deselect all documents in the table before using this chat mode",
                "info": {
                    "sources": [],
                    "model": "",
                    "nodedetails": [],
                    "total_tokens": 0,
                    "response_time": 0,
                    "mode": chat_mode_settings["mode"],
                    "entities": [],
                    "metric_details": [],
                },
                "user": "chatbot"
            }
        else:
            result = process_chat_response(messages,history, question, model, graph, parsed_document_names,chat_mode_settings)

    result["session_id"] = session_id
    
    return result

def get_chat_histories(graph, limit=50, offset=0):
    """
    Retrieves all chat histories from the Neo4j database with pagination.
    
    Args:
        graph: Neo4jGraph instance
        limit (int): Maximum number of chat histories to return (default: 50)
        offset (int): Number of chat histories to skip (default: 0)
        
    Returns:
        dict: Contains chat histories with metadata and pagination info
    """
    try:
        logging.info(f"Retrieving chat histories with limit={limit}, offset={offset}")
        
        # Query to get all chat session IDs with their metadata
        query = """
        MATCH (s:__Session__)
        RETURN s.sessionId as session_id,
               s.createdAt as created_at,
               s.updatedAt as updated_at,
               size([(s)-[:HAS_MESSAGE]->(m) | m]) as message_count
        ORDER BY s.updatedAt DESC
        SKIP $offset
        LIMIT $limit
        """
        
        result = graph.query(query, {"limit": limit, "offset": offset})
        
        # Get total count for pagination
        count_query = """
        MATCH (s:__Session__)
        RETURN count(s) as total_count
        """
        count_result = graph.query(count_query)
        total_count = count_result[0]["total_count"] if count_result else 0
        
        # Process the results
        chat_histories = []
        for record in result:
            chat_history = {
                "session_id": record["session_id"],
                "created_at": record["created_at"].isoformat() if record["created_at"] else None,
                "updated_at": record["updated_at"].isoformat() if record["updated_at"] else None,
                "message_count": record["message_count"]
            }
            chat_histories.append(chat_history)
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 0
        current_page = (offset // limit) + 1 if limit > 0 else 1
        
        response_data = {
            "chat_histories": chat_histories,
            "pagination": {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": current_page,
                "limit": limit,
                "offset": offset,
                "has_next": offset + limit < total_count,
                "has_previous": offset > 0
            }
        }
        
        logging.info(f"Successfully retrieved {len(chat_histories)} chat histories out of {total_count} total")
        return response_data
        
    except Exception as e:
        logging.error(f"Error retrieving chat histories: {e}")
        raise Exception(f"Failed to retrieve chat histories: {str(e)}")

def get_chat_history_by_session_id(graph, session_id):
    """
    Retrieves a specific chat history by session ID.
    
    Args:
        graph: Neo4jGraph instance
        session_id (str): The session ID to retrieve
        
    Returns:
        dict: Contains chat history details and messages
    """
    try:
        logging.info(f"Retrieving chat history for session: {session_id}")
        
        # Query to get session metadata
        session_query = """
        MATCH (s:__Session__ {sessionId: $session_id})
        RETURN s.sessionId as session_id,
               s.createdAt as created_at,
               s.updatedAt as updated_at
        """
        
        session_result = graph.query(session_query, {"session_id": session_id})
        
        if not session_result:
            raise Exception(f"Chat history not found for session: {session_id}")
        
        session_data = session_result[0]
        
        # Query to get messages for this session
        messages_query = """
        MATCH (s:__Session__ {sessionId: $session_id})-[:HAS_MESSAGE]->(m:__Message__)
        RETURN m.type as message_type,
               m.content as content,
               m.additionalKwargs as additional_kwargs,
               m.createdAt as created_at
        ORDER BY m.createdAt ASC
        """
        
        messages_result = graph.query(messages_query, {"session_id": session_id})
        
        # Process messages
        messages = []
        for record in messages_result:
            message = {
                "type": record["message_type"],
                "content": record["content"],
                "additional_kwargs": record["additional_kwargs"] if record["additional_kwargs"] else {},
                "created_at": record["created_at"].isoformat() if record["created_at"] else None
            }
            messages.append(message)
        
        response_data = {
            "session_id": session_data["session_id"],
            "created_at": session_data["created_at"].isoformat() if session_data["created_at"] else None,
            "updated_at": session_data["updated_at"].isoformat() if session_data["updated_at"] else None,
            "message_count": len(messages),
            "messages": messages
        }
        
        logging.info(f"Successfully retrieved chat history for session {session_id} with {len(messages)} messages")
        return response_data
        
    except Exception as e:
        logging.error(f"Error retrieving chat history for session {session_id}: {e}")
        raise Exception(f"Failed to retrieve chat history: {str(e)}")

def delete_chat_history(graph, session_id):
    """
    Deletes a specific chat history by session ID.
    
    Args:
        graph: Neo4jGraph instance
        session_id (str): The session ID to delete
        
    Returns:
        dict: Success message
    """
    try:
        logging.info(f"Deleting chat history for session: {session_id}")
        
        # Delete the session and all its messages
        delete_query = """
        MATCH (s:__Session__ {sessionId: $session_id})
        OPTIONAL MATCH (s)-[:HAS_MESSAGE]->(m:__Message__)
        DELETE m, s
        """
        
        result = graph.query(delete_query, {"session_id": session_id})
        
        logging.info(f"Successfully deleted chat history for session {session_id}")
        return {
            "session_id": session_id,
            "message": "Chat history deleted successfully",
            "deleted": True
        }
        
    except Exception as e:
        logging.error(f"Error deleting chat history for session {session_id}: {e}")
        raise Exception(f"Failed to delete chat history: {str(e)}")
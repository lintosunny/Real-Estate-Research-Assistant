import streamlit as st
import time
from typing import List

from real_estate_assistant.config import settings
from real_estate_assistant.services.rag_service import rag_service
from real_estate_assistant.utils.logger import logger
from real_estate_assistant.utils.exceptions import URLProcessingError, VectorStoreError, LLMError, ValidationError
from real_estate_assistant.utils.validators import sanitize_input

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'urls_processed' not in st.session_state:
        st.session_state.urls_processed = []
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []


def display_header():
    """Display application header and information"""
    st.set_page_config(
        page_title=settings.app_name,
        page_icon="🏙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title(f"🏙️ {settings.app_name}")
    st.markdown(f"*Version {settings.app_version}*")
    
    with st.expander("ℹ️ About This Tool"):
        st.markdown("""
        This tool helps you research real estate topics by:
        1. **Loading Content**: Input URLs of real estate articles or reports
        2. **Processing Data**: Creates searchable knowledge base using AI embeddings
        3. **Answering Questions**: Ask questions and get AI-powered answers with sources
        
        **Supported Sources**: News articles, reports, blogs, and other web content
        """)


def display_sidebar():
    """Display sidebar with URL inputs and controls"""
    st.sidebar.header("📊 Data Sources")
    
    # URL inputs
    urls = []
    for i in range(1, 6):  # Support up to 5 URLs
        url = st.sidebar.text_input(
            f"URL {i}",
            key=f"url_{i}",
            placeholder="https://example.com/article"
        )
        if url:
            urls.append(sanitize_input(url))
    
    # Process URLs button
    process_button = st.sidebar.button(
        "🔄 Process URLs",
        type="primary",
        help="Load and process content from the provided URLs"
    )
    
    # Display current status
    st.sidebar.subheader("📈 Status")
    collection_info = rag_service.get_collection_info()
    
    if collection_info["status"] == "initialized":
        st.sidebar.success(f"✅ Ready ({collection_info['count']} documents)")
        st.session_state.processing_complete = True
    elif collection_info["status"] == "not_initialized":
        st.sidebar.warning("⏳ Waiting for data processing")
        st.session_state.processing_complete = False
    else:
        st.sidebar.error("❌ System error")
        st.session_state.processing_complete = False
    
    # Health check in sidebar
    with st.sidebar.expander("🔧 System Health"):
        health = rag_service.health_check()
        for component, status in health.items():
            if status == "healthy":
                st.success(f"✅ {component.replace('_', ' ').title()}")
            elif status == "unhealthy":
                st.error(f"❌ {component.replace('_', ' ').title()}")
            else:
                st.warning(f"⚠️ {component.replace('_', ' ').title()}: {status}")
    
    return urls, process_button


def process_urls_with_ui(urls: List[str]):
    """Process URLs with real-time UI updates"""
    try:
        # Validate inputs
        if not urls:
            st.error("❌ Please provide at least one valid URL")
            return
        
        # Create progress containers
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        # Process URLs with progress updates
        total_steps = 5
        current_step = 0
        
        for status_message in rag_service.process_urls(urls):
            current_step += 1
            progress_bar.progress(current_step / total_steps)
            status_container.info(f"**Status:** {status_message}")
            time.sleep(0.5)  # Small delay for better UX
        
        # Success message
        st.session_state.processing_complete = True
        st.session_state.urls_processed = urls
        st.success("🎉 **Processing Complete!** You can now ask questions about the content.")
        
        # Log success
        logger.info(f"Successfully processed {len(urls)} URLs")
        
    except ValidationError as e:
        st.error(f"❌ **Validation Error:** {str(e)}")
        logger.error(f"Validation error: {str(e)}")
        
    except URLProcessingError as e:
        st.error(f"❌ **URL Processing Error:** {str(e)}")
        st.info("💡 **Tip:** Make sure URLs are accessible and contain readable content")
        logger.error(f"URL processing error: {str(e)}")
        
    except VectorStoreError as e:
        st.error(f"❌ **Database Error:** {str(e)}")
        st.info("💡 **Tip:** Try restarting the application")
        logger.error(f"Vector store error: {str(e)}")
        
    except Exception as e:
        st.error(f"❌ **Unexpected Error:** {str(e)}")
        st.info("💡 **Tip:** Check the logs for more details")
        logger.error(f"Unexpected error during URL processing: {str(e)}")


def display_query_interface():
    """Display query interface and handle questions"""
    st.header("💬 Ask Questions")
    
    # Query input
    query = st.text_input(
        "What would you like to know?",
        placeholder="e.g., What are the current mortgage rates? What factors affect real estate prices?",
        help="Ask questions about the content you've processed"
    )
    
    # Search button
    search_button = st.button(
        "🔍 Get Answer",
        type="primary",
        disabled=not st.session_state.processing_complete
    )
    
    if search_button and query:
        try:
            # Sanitize query
            clean_query = sanitize_input(query)
            
            # Show loading spinner
            with st.spinner("🤔 Thinking..."):
                start_time = time.time()
                answer, sources = rag_service.generate_answer(clean_query)
                end_time = time.time()
            
            # Display results
            st.subheader("💡 Answer")
            st.write(answer)
            
            # Display sources
            if sources.strip():
                st.subheader("📚 Sources")
                source_lines = [line.strip() for line in sources.split("\n") if line.strip()]
                for source in source_lines:
                    st.write(f"• {source}")
            else:
                st.info("No specific sources identified for this answer")
            
            # Display performance info
            response_time = end_time - start_time
            st.caption(f"⏱️ Response time: {response_time:.2f} seconds")
            
            # Add to query history
            st.session_state.query_history.append({
                "query": clean_query,
                "answer": answer,
                "sources": sources,
                "timestamp": time.time()
            })
            
            # Log successful query
            logger.info(f"Successfully answered query: {clean_query[:50]}...")
            
        except ValidationError as e:
            st.error(f"❌ **Invalid Query:** {str(e)}")
            
        except LLMError as e:
            st.error(f"❌ **AI Error:** {str(e)}")
            st.info("💡 **Tip:** Try rephrasing your question")
            
        except VectorStoreError as e:
            st.error(f"❌ **Database Error:** {str(e)}")
            st.info("💡 **Tip:** Make sure you have processed URLs first")
            
        except Exception as e:
            st.error(f"❌ **Unexpected Error:** {str(e)}")
            logger.error(f"Unexpected error during query processing: {str(e)}")
    
    elif search_button and not query:
        st.warning("⚠️ Please enter a question")


def display_query_history():
    """Display query history"""
    if st.session_state.query_history:
        with st.expander(f"📝 Query History ({len(st.session_state.query_history)} queries)"):
            for i, item in enumerate(reversed(st.session_state.query_history[-10:])):  # Show last 10
                st.markdown(f"**Q{len(st.session_state.query_history)-i}:** {item['query']}")
                st.markdown(f"**A:** {item['answer'][:200]}{'...' if len(item['answer']) > 200 else ''}")
                st.markdown("---")


def display_footer():
    """Display footer information"""
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔒 Privacy:** Data is processed locally")
    
    with col2:
        st.markdown("**⚡ AI Model:** Llama 3.3 via Groq")
    
    with col3:
        st.markdown("**🔄 Vector DB:** ChromaDB with HuggingFace embeddings")


def main():
    """Main application function"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Display header
        display_header()
        
        # Display sidebar and get inputs
        urls, process_button = display_sidebar()
        
        # Handle URL processing
        if process_button:
            process_urls_with_ui(urls)
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Query interface
            display_query_interface()
            
            # Query history
            display_query_history()
        
        with col2:
            # Display processed URLs
            if st.session_state.urls_processed:
                st.subheader("📋 Processed URLs")
                for i, url in enumerate(st.session_state.urls_processed, 1):
                    st.write(f"{i}. {url}")
            
            # Display tips
            st.subheader("💡 Tips")
            st.markdown("""
            - Use specific questions for better results
            - Include context in your questions
            - Try different phrasings if needed
            - Check sources for verification
            - Ask follow-up questions for deeper insights
            - Reference specific time periods or locations
            """)
            
            # Display example questions
            with st.expander("❓ Example Questions"):
                st.markdown("""
                **Market Analysis:**  
                - "What are the current mortgage rates?"  
                - "How do interest rates affect home prices?"  

                **Investment Insights:**  
                - "What are the best real estate investment opportunities?"  
                - "Compare rental vs. buying markets"  

                **Trend Analysis:**  
                - "What are emerging real estate trends for 2024?"  
                - "How is the housing market performing this year?"  

                **Regional Questions:**  
                - "What's happening in the San Francisco housing market?"  
                - "Compare real estate prices across different cities"  
                """)

        # Display footer
        display_footer()

    except Exception as e:
        st.error(f"❌ **Application Error:** {str(e)}")
        logger.error(f"Application error: {str(e)}")
        st.info("💡 **Tip:** Please refresh the page and try again")

if __name__ == "__main__":
    main()
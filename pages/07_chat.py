"""Interactive chat module for AWS migration and modernization analysis."""

import streamlit as st
from mem0 import Memory

from utils.bedrock_client import invoke_bedrock_model_without_reasoning
from utils.config import get_chat_model_config, get_memory_model_config, load_css, get_embedder_config_to_initialize_mem0, get_vector_store_config_initialize_mem0

# Constants
MAX_MESSAGES = 10  # 5 interactions = 10 messages (5 user + 5 assistant)


def initialize_mem0():
    """Initialize Mem0 with Bedrock configuration using Claude 3.7 Sonnet for memory operations"""
    try:
        model_config = get_memory_model_config()  # Get memory-specific config
        
        config = {
            "llm": {
                "provider": "aws_bedrock",
                "config": {
                    "model": model_config["model_id"],  
                    "temperature": model_config["temperature"],  
                    "max_tokens": model_config["max_tokens"], 
                },
            },
            "embedder": get_embedder_config_to_initialize_mem0(),
            "vector_store": get_vector_store_config_initialize_mem0(),
        }
        return Memory.from_config(config)
    except Exception as e:
        st.error(f"Failed to initialize Mem0: {str(e)}")
        st.info("Memory functionality will be disabled. Chat will work without memory.")
        return None


def check_message_context(messages):
    """
    Check message context and return appropriate status
    Returns (context_status, message_count):
        context_status:
            0 = first message
            1 = has recent context
            2 = needs memory search
        message_count: number of existing messages
    """
    message_count = len(messages) if messages else 0

    if message_count == 0:
        return (0, 0)  # First message
    elif message_count < MAX_MESSAGES:
        return (1, message_count)  # Has recent context
    else:
        return (2, message_count)  # Need memory search


# Load external CSS
load_css()

# Initialize Mem0
if "memory" not in st.session_state:
    st.session_state.memory = initialize_mem0()

# Initialise chat history in session state (only last 10 messages for display)
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "selected_context" not in st.session_state:
    st.session_state.selected_context = None

if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user"

# Page header
st.markdown(
    """
<div class="page-header">
    <h1>Interaction with analysis</h1>
    <p>Interaction with migration and modernisation analysis</p>
</div>
""",
    unsafe_allow_html=True,
)

# Get model configuration
model_config = get_chat_model_config()  # Use chat-specific config

# Define available contexts
available_contexts = {
    "Inventory Analysis": "inventory_analysis",
    "Modernisation Recommendations": "modz_analysis",
    "On-Premises Architecture": "onprem_architecture",
    "Migration Strategy": "strategy_text",
    "Resource Planning": "resource_planning_data",
}

# Context selection
st.subheader("Select a scenario to start conversation")
selected_context_name = st.selectbox(
    "Choose which analysis you want to discuss:",
    options=list(available_contexts.keys()),
)

context_key = available_contexts[selected_context_name]

# Check if selected context has data
if context_key in st.session_state and st.session_state[context_key] != context_key:
    context_data = st.session_state[context_key]

    # Display context info
    st.info(f"**Active Context:** {selected_context_name}")
    
    # Memory status indicator (for debugging)
    # if st.session_state.memory:
    #     try:
    #         all_memories = st.session_state.memory.get_all(user_id=st.session_state.user_id)
    #         memory_count = len(all_memories.get("results", [])) if all_memories else 0
    #         if memory_count > 0:
    #             # Each memory entry represents a conversation pair, so display accordingly
    #             st.success(f"Memory active: {memory_count} memory entries stored")
    #         else:
    #             st.info("Memory active: No previous conversations")
    #     except Exception as e:
    #         st.warning(f"Memory status unknown: {str(e)}")
    # else:
    #     st.warning("Memory not available")

    with st.expander("View Current Context Data"):
        st.markdown(context_data)

    st.divider()

    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the analysis..."):
        # User message to display
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Check message context to determine if Mem0 search is needed
                context_status, message_count = check_message_context(
                    st.session_state.chat_messages[:-1]
                )

                mem0_context = ""

                # Only search Mem0 if memory is initialized and have enough conversation history
                if st.session_state.memory and message_count >= 4:  # Search after 2 interactions (4 messages)
                    print(f"\n=== Searching Mem0 for: {prompt} ===")
                    print(f"User ID: {st.session_state.user_id}")
                    try:
                        # Perform search for relevant conversation history
                        search_results = st.session_state.memory.search(
                            prompt, user_id=st.session_state.user_id, limit=5
                        )
                        print(f"Raw search results: {search_results}")
                        
                        # Extract results and filter by current context
                        if search_results and isinstance(search_results, dict) and "results" in search_results:
                            results = search_results["results"]
                            print(f"Found {len(results)} search results")
                            
                            # Filter results by current context if metadata exists
                            relevant_results = []
                            for result in results:
                                if "metadata" in result and result["metadata"].get("context") == selected_context_name:
                                    relevant_results.append(result)
                                elif "metadata" not in result:  # Include results without metadata for backward compatibility
                                    relevant_results.append(result)
                            
                            if len(relevant_results) > 0:
                                mem0_context = "\n\nRelevant conversation history:\n"
                                for result in relevant_results[:3]:  # Top 3 most relevant
                                    if "memory" in result:
                                        mem0_context += f"- {result['memory']}\n"
                                        print(f"Added memory: {result['memory'][:50]}...")
                                
                                print(f"Final context length: {len(mem0_context)}")
                                st.info(f"Retrieved {len(relevant_results[:3])} relevant memories from {selected_context_name} context")
                            else:
                                print(f"No relevant results found for context: {selected_context_name}")
                                st.info("No relevant conversation history found for this context")
                        else:
                            print(f"Unexpected search result format: {type(search_results)}")
                            
                    except Exception as e:
                        print(f"Error searching Mem0: {e}")
                        import traceback
                        print(f"Full traceback: {traceback.format_exc()}")
                        st.warning("Could not retrieve conversation history.")
                elif not st.session_state.memory:
                    if message_count >= 4:
                        st.info("Memory search not available - using current context only.")

                # Prompt with context
                context_indicator = ""
                if mem0_context:
                    context_indicator = " (with conversation history)"
                
                full_prompt = f"""You are an AWS migration and modernisation expert assistant with deep knowledge of AWS transformation strategies and best practices.

                Context Information ({selected_context_name}):
                {context_data}
                {mem0_context}

                User Question: {prompt}

                Instructions: Please provide a comprehensive, accurate response based on the context provided above. Your response should:

                - Only draw upon the specific context information to address the user's question
                - Apply AWS migration and modernisation best practices and frameworks in response
                - Use clear, professional language appropriate for technical audiences
                - Clearly indicate the source of your information:
                    If answering from the provided context, state: "Based on the context provided..." or "According to the information available..."
                    If supplementing with general AWS knowledge, explicitly state: "Based on general AWS best practices..." or "From AWS migration expertise (not in the provided context)..."
                    If the question cannot be answered from the available context, respond with: "I cannot find specific information about this in the provided context. However, based on general AWS migration knowledge, [provide relevant information]. For a more accurate answer specific to your situation, please provide additional context about [specify what's needed]."

                    Ensure your response is actionable, well-structured, and maintains transparency about information sources"""

                # Invoke model
                response = invoke_bedrock_model_without_reasoning(full_prompt)

                if response:
                    st.markdown(response)
                    # Add assistant response to display
                    st.session_state.chat_messages.append(
                        {"role": "assistant", "content": response}
                    )

                    # Store conversation pair in Mem0 if available
                    if st.session_state.memory:
                        try:
                            conversation_pair = [
                                {"role": "user", "content": prompt},
                                {"role": "assistant", "content": response},
                            ]
                            print("\n=== Storing in Mem0 ===")
                            print(f"User message: {prompt}")
                            print(f"Assistant response: {response[:100]}...")  # Truncate for readability
                            
                            # Store the conversation
                            result = st.session_state.memory.add(
                                conversation_pair,
                                user_id=st.session_state.user_id,
                                metadata={"context": selected_context_name},
                            )
                            print(f"Storage result: {result}")
                            
                            # Verify storage by checking total memories
                            all_memories = st.session_state.memory.get_all(user_id=st.session_state.user_id)
                            memory_count = len(all_memories.get("results", [])) if all_memories else 0
                            print(f"Total memory entries stored: {memory_count}")
                            
                        except Exception as e:
                            print(f"Error storing in Mem0: {e}")
                            st.warning("Could not save conversation to memory.")

                    # Keep only last 5 interactions (10 messages)
                    if len(st.session_state.chat_messages) > MAX_MESSAGES:
                        st.session_state.chat_messages = (
                            st.session_state.chat_messages[-MAX_MESSAGES:]
                        )
                else:
                    error_msg = (
                        "I apologise, but I'm unable to generate a response "
                        "at the moment."
                    )
                    st.markdown(error_msg)
                    st.session_state.chat_messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

    # Clear chat button with improved functionality
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Clear Chat History"):
            st.session_state.chat_messages = []
            st.success("Chat history cleared.")
            st.rerun()
    
    with col2:
        if st.button("Clear All Memory", type="secondary"):
            if st.session_state.memory:
                try:
                    # Clear only memories for current context to be more precise
                    all_memories = st.session_state.memory.get_all(user_id=st.session_state.user_id)
                    deleted_count = 0
                    
                    if all_memories and "results" in all_memories:
                        for memory in all_memories["results"]:
                            # Delete memories that match current context or have no context metadata
                            memory_context = memory.get("metadata", {}).get("context")
                            if memory_context == selected_context_name or memory_context is None:
                                st.session_state.memory.delete(memory["id"])
                                deleted_count += 1
                    
                    st.success(f"Cleared {deleted_count} memory entries for {selected_context_name}.")
                    st.session_state.chat_messages = []
                    st.rerun()
                    
                except Exception as e:
                    print(f"Error clearing Mem0: {e}")
                    st.error("Could not clear memory. Please try again.")
            else:
                st.warning("Memory not available to clear.")

else:
    st.warning(
        f"No data available for **{selected_context_name}**. "
        f"Please complete the relevant analysis first."
    )
    st.info("""
    **Available Analysis Pages:**
    - Inventory Analysis: Run the modernisation opportunity analysis
    - Modernisation Recommendations: Generate modernisation recommendations
    - On-Premises Architecture: Upload and analyse architecture diagrams
    - Migration Strategy: Develop migration patterns and planning
    - Resource Planning: Plan resources for migration waves
    """)

import streamlit as st
from openai import OpenAI
from pinecone import Pinecone

# 1. Page Configuration
st.set_page_config(page_title="Aeolianlux AI", page_icon="🤖")
st.title("Aeolianlux Intelligence")
st.caption("Ask me about UAE Jobs & International Clients.")

# 2. Connect
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    index = pc.Index("aeolianlux-index") 
except Exception as e:
    st.error(f"Connection Error: {e}. Did you set up the secrets?")
    st.stop()

# 3. Chat History
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I can help you find clients and job opportunities in our database. What are you looking for?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. Input
if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # A. Embed
        response = client.embeddings.create(
            input=prompt,
            model="text-embedding-3-small"
        )
        query_vector = response.data[0].embedding

        # B. Search
        search_response = index.query(
            vector=query_vector,
            top_k=5, 
            include_metadata=True
        )

        # C. Context
        context_text = ""
        for match in search_response['matches']:
            if 'text' in match['metadata']:
                context_text += match['metadata']['text'] + "\n---\n"

        # D. Answer (UPDATED INSTRUCTION)
        system_prompt = f"""You are an intelligent consultant for Aeolianlux.
        The user is asking about Jobs, Clients, or Business Opportunities.
        
        The Context below contains a list of Companies/Clients. 
        TREAT THESE COMPANIES AS POTENTIAL JOB OPPORTUNITIES OR LEADS.
        
        Context from Database:
        {context_text}
        
        Instructions:
        1. If the user asks for "Jobs" in a specific location (like Dubai), list the companies found in the context as potential opportunities.
        2. Provide details (Phone/Email) if available in the context.
        3. Be professional and encouraging.
        4. If the context is empty, politely say you don't have records for that specific request yet.
        """

        openai_response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        
        bot_reply = openai_response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.chat_message("assistant").write(bot_reply)

    except Exception as e:
        st.error(f"An error occurred: {e}")

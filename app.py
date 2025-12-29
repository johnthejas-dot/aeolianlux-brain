import streamlit as st
from openai import OpenAI
from pinecone import Pinecone

# 1. Page Configuration
st.set_page_config(page_title="Aeolianlux Luxury Living", page_icon="✨")
st.title("Dubai Luxury Living")
st.caption("Stay • Shop • Food")

# 2. Connect
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    index = pc.Index("aeolianlux-index") 
except Exception as e:
    st.error(f"Connection Error: {e}. Did you set up the secrets?")
    st.stop()

# 3. Chat History (UPDATED GREETING)
if "messages" not in st.session_state:
    st.session_state["messages"] = [{
        "role": "assistant", 
        "content": "Hello! I can help you find Exotic Luxury places to stay, excellent restaurants, and where to buy Luxury special gifts. What are you looking for?"
    }]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. Input (UPDATED PLACEHOLDER)
if prompt := st.chat_input("Ask me about Dubai Luxury life..."):
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

        # D. Answer
        system_prompt = f"""You are a Luxury Concierge for Dubai.
        
        Context from Database:
        {context_text}
        
        Instructions:
        1. Answer the user's question using the Context provided.
        2. If the user asks for hotels, restaurants, or shopping, recommend the best options from the database.
        3. Maintain a polite, premium, and helpful tone.
        4. If the answer is not in the context, offer to connect them to the Aeolianlux team for a bespoke arrangement.
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

import os
import json
from datetime import datetime
import streamlit as st
from openai import OpenAI

# Use Streamlit Secrets for secure API key access
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Prompt builder
def get_prompt(topic):
    return f"""
You are a top-tier SEO content writer. Write a 2000-word blog post for entrepreneurs aged 30–45.

Guidelines:
- Use primary keyword 3–4 times in quotes
- Use secondary keywords as H2 (also in quotes)
- Friendly, clear tone
- Use Markdown format
- Mention tools, examples, stats
- No technical jargon or AI mention

Topic: "{topic}"

Respond only in JSON:
{{
  "title": "...",
  "meta_description": "...",
  "keywords": ["...", "..."],
  "content": "...",
  "cta": "..."
}}
"""

# Blog generator using GPT-4
def generate_blog(topic):
    prompt = get_prompt(topic)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=3500
    )
    return json.loads(response.choices[0].message.content)

# Blog image generation using DALL·E 3
def generate_image(topic):
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Eye-catching blog illustration: {topic}",
        size="1024x1024",
        n=1
    )
    return response.data[0].url

# Save the generated blog as a .md file
def save_file(data):
    os.makedirs("blogs", exist_ok=True)
    slug = data['title'].lower().replace(" ", "-")
    path = f"blogs/{datetime.now().strftime('%Y-%m-%d')}-{slug}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {data['title']}\n\n")
        f.write(f"**Meta Description:** {data['meta_description']}\n\n")
        f.write(f"**Keywords:** {', '.join(data['keywords'])}\n\n")
        f.write(data['content'] + "\n\n---\n\n**CTA:** " + data['cta'])
    return path

# ----------------------------
# Streamlit UI
# ----------------------------

st.set_page_config(page_title="HustleOS Blog Agent", layout="centered")
st.title("🛠️ HustleOS - AI Blog Agent")

topic = st.text_input("Enter blog topic and press enter")

if st.button("Generate"):
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Working on your blog..."):
            blog = generate_blog(topic)
            image_url = generate_image(topic)
            blog['content'] = f"![Blog Image]({image_url})\n\n" + blog['content']
            file_path = save_file(blog)

        st.success("✅ Blog Ready!")
        st.subheader(blog['title'])
        st.markdown(blog['content'], unsafe_allow_html=True)
        st.markdown(f"---\n**CTA:** {blog['cta']}")
        with open(file_path, "r", encoding="utf-8") as file:
            st.download_button("⬇️ Download Blog", file.read(), file_name=file_path)

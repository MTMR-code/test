import streamlit as st

st.title("🎈 My First Streamlit App")
st.write("Hello, World!")

name = st.text_input("あなたの名前を入力してください")
if name:
    st.write(f"こんにちは、{name}さん！")
    
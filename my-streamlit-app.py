import streamlit as st

st.title("🎈 My First Streamlit App")
st.write("Hello, World!")

name = st.text_input("あなたの名前を入力してください")
residence = st.text_input("あなたの居住地を入力してください")

if name and residence:
    st.write(f"こんにちは、{name}さん！")
    st.write(f"居住地: {residence}")
elif name:
    st.write(f"こんにちは、{name}さん！")
    st.write("居住地も入力してください。")
elif residence:
    st.write(f"居住地: {residence}")
    st.write("名前も入力してください。")
    
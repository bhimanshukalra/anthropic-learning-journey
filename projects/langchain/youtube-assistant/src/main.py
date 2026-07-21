import streamlit as st
import helper
import textwrap

st.title("Youtube assistant")

with st.sidebar:
    with st.form(key="my_form"):
        video_url = st.sidebar.text_area(label="What is the video URL?", max_chars=50)
        query = st.sidebar.text_area(
            label="What is the question?", max_chars=50, key="query"
        )
        submit_button = st.form_submit_button(label="Submit")

if query and video_url:
    db = helper.create_vector_db_from_youtube_url(video_url)
    if db:
        response = helper.get_response_from_query(db, query)
    else:
        response = "Couln't process the video"

    st.subheader("Answer:")
    st.markdown(response, width=100)

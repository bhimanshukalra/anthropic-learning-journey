import streamlit as st
import src.helper as helper


def main():
    st.title("🐶 Pets Name Generator")

    animal_type = st.sidebar.selectbox(
        "What is your pet?", ("Dog", "Cat", "Hamster", "Rat", "Snake", "Lizard", "Cow")
    )

    pet_color = st.sidebar.text_area(
        label=f"What color is your {animal_type}?",
        max_chars=25,
    )

    if pet_color:
        response = helper.generate_pet_name(animal_type, pet_color)
        st.markdown(response)


if __name__ == "__main__":
    main()

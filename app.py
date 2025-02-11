import streamlit as st
import os
import pickle
import json

# Define where images are stored
IMAGE_DIR = "./images"
ANNOTATION_DIR = "./annotator_files"

# Sample data: Map images to their captions
with open("/home/as5957/vwp_metric/annotations/task_1.pkl", "rb") as f:
    data = pickle.load(f)

with open("id_indices.pkl", "rb") as f:
    indexes_id = pickle.load(f)


# Ensure images exist
image_files = list(data.keys())

# Create annotation directory if not exists
os.makedirs(ANNOTATION_DIR, exist_ok=True)

# Initialize session state for navigation and annotator ID
if "page" not in st.session_state:
    st.session_state.page = "select_id"  # Start at the annotator ID selection page
if "annotator_id" not in st.session_state:
    st.session_state.annotator_id = None  # Annotator ID starts as None

# --- Page 1: Annotator ID Selection ---
if st.session_state.page == "select_id":
    st.title("Image Caption Annotation Task 1")
    st.markdown(
         
        """
        ##
        Welcome to the caption annotation task! Please follow the instructions below:

        Please select your assigned annotator ID to begin. Once you proceed, you **cannot change your ID**.  
        
        **Annotation Task Instructions** 📝
        1. Each image has 6 captions. **Your task is to rank each caption on a scale of 1 through 6 where 1 refers to the captions that have the most literal description of the image and 6 refers to captions that have the most abstract descriptions of the image.**
        For clarity, literal descriptions of images will provide a straightforward, factual account of what is visually present in the image. Meanwhile abstract descriptions take more creative liberty, conveying the essence, emotions, or symbolic meaning rather than capturing the concrete details.
        2. **Each rank should be unique**—no duplicate rankings for a single image.
        3. **Select a rank for every caption** before submitting.
        4. **Click "Submit"** once you have ranked all captions for an image.
        5. Your progress is saved automatically, and you can resume later if needed (make sure to enter the same annotator id below).

        ---
        """
    )

    # Allow annotator to select an ID
    annotator_ids = ["1", "2", "3", "4", "5"]
    selected_id = st.selectbox("Select your annotator ID", ["Select an ID"] + annotator_ids, key="selected_id")

    # Proceed button
    if selected_id != "Select an ID":
        if st.button("Proceed"):
            st.session_state.annotator_id = selected_id  # Set the ID in session state
            st.session_state.page = "annotation"  # Move to annotation page
            st.rerun()  # Refresh the page to update the UI

# --- Page 2: Annotation Task ---
elif st.session_state.page == "annotation":
    annotator_id = st.session_state.annotator_id  # Get stored annotator ID    
    st.title(f"Annotator {annotator_id} - Annotation Task")

    # Define file path for annotator's JSON file
    annotation_file = os.path.join(ANNOTATION_DIR, f"{annotator_id}_annotations.json")

    # Load existing annotations if available
    if os.path.exists(annotation_file):
        with open(annotation_file, "r") as f:
            annotations = json.load(f)
    else:
        annotations = {}

    # Filter out images already annotated
    annotator_images = [image_files[i] for i in indexes_id[int(annotator_id)]][:2]
    remaining_images = [img for img in annotator_images if img not in annotations]

    if not remaining_images:
        st.success("You have completed all annotations! 🎉")
    else:
        for img_file in remaining_images:
            img_path = os.path.join(IMAGE_DIR, img_file)
            st.image(img_path, use_container_width=True)

            st.write("Rank the captions from 1 (most literal) to 6 (most abstract):")

            available_ranks = [1, 2, 3, 4, 5, 6]
            selected_ranks = {}

            for caption in data[img_file]:
                selected_ranks[caption] = st.selectbox(
                    f'"{caption}"',
                    ["Select a rank"] + available_ranks,
                    key=f"{img_file}_{caption}"
                )

            # Validation checks
            selected_values = [v for v in selected_ranks.values() if v != "Select a rank"]
            has_duplicates = len(set(selected_values)) != len(selected_values)
            has_unselected = "Select a rank" in selected_ranks.values()

            submit_disabled = has_duplicates or has_unselected

            if has_duplicates:
                st.warning("Each caption must have a unique rank!")

            if has_unselected:
                st.warning("All captions must be ranked before submission!")

            if st.button("Submit", key=img_file, disabled=submit_disabled):
                # Save the new annotations
                annotations[img_file] = {caption: rank for caption, rank in selected_ranks.items()}

                # Write updated annotations to JSON
                with open(annotation_file, "w") as f:
                    json.dump(annotations, f, indent=4)

                st.success("Saved! ✅")
                # st.rerun()  # Refresh after each submission

       
        st.success("🎉 You have completed all annotations! Thank you for your work.")


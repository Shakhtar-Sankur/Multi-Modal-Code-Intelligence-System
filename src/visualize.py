import streamlit as st
import requests
import logging

def main():
    logger = logging.getLogger(__name__)
    st.title("Multi-Modal Code Intelligence System")
    
    # Input code
    code = st.text_area("Enter Python code:", height=300)
    
    if st.button("Analyze"):
        if code:
            try:
                # Call API
                response = requests.post('http://localhost:5000/analyze', json={'code': code})
                results = response.json()
                
                # Display results
                st.subheader("Analysis Results")
                st.write(f"Semantic Class: {results['semantic_class']}")
                st.write(f"Confidence: {results['confidence']:.2f}")
                st.write("Metadata:")
                for key, value in results['metadata'].items():
                    st.write(f"{key}: {value}")
                
                logger.info("Visualization displayed successfully")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Visualization error: {str(e)}")
        else:
            st.warning("Please enter code to analyze.")

if __name__ == "__main__":
    main()
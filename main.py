import pandas as pd
import streamlit as st
from io import BytesIO

st.title("lncRNA Gene Filter Tool")

# File uploader
uploaded_file = st.file_uploader("Upload Excel File", type=["xls", "xlsx"])

# Input box for mRNA name
custom_text = st.text_input("Enter mRNA name to appear in Column A of the Excel output")

if uploaded_file and custom_text:
    try:
        # Detect file type and set appropriate engine
        file_type = uploaded_file.name.split('.')[-1].lower()
        if file_type == 'xls':
            engine = 'xlrd'
        elif file_type == 'xlsx':
            engine = 'openpyxl'
        else:
            st.error("Unsupported file type.")
            st.stop()

        # Read the file, skipping the first 5 rows
        df = pd.read_excel(uploaded_file, skiprows=5, header=None, engine=engine)

        # Extract relevant columns D and E (index 3 and 4)
        df_filtered = df[[3, 4]]
        df_filtered.columns = ['geneName', 'geneType']

        # Filter for lncRNA and remove duplicates (both geneName + geneType)
        df_lncRNA = df_filtered[df_filtered['geneType'] == 'lncRNA'].drop_duplicates()

        # Final output: mRNA column + geneName column
        output_df = pd.DataFrame({
            'mRNA': [custom_text] * len(df_lncRNA),
            'GeneName': df_lncRNA['geneName'].values
        })

        st.success(f"Filtered {len(output_df)} unique lncRNA entries.")
        st.dataframe(output_df)

        # Button to download as Excel
        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='lncRNA')
            return output.getvalue()

        excel_data = convert_df_to_excel(output_df)
        st.download_button(
            label="Download Excel File",
            data=excel_data,
            file_name="filtered_lncRNA_genes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")

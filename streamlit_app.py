import streamlit as st
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import pandas as pd

# Replace with your credentials
endpoint = "https://azureumkmworkdocumentintelligence.cognitiveservices.azure.com/"
api_key = "e7a714ba68e1475a988ba60e0019850f"

def analyze_document(file_obj):
 document_analysis_client = DocumentAnalysisClient(
   endpoint=endpoint, credential=AzureKeyCredential(api_key)
 )
 
 # Check for file type (image or PDF)
 if file_obj.type == 'image/jpeg' or file_obj.type == 'image/png':
  poller = document_analysis_client.begin_analyze_document("prebuilt-invoice", file_obj)
 elif file_obj.type == 'application/pdf':
  # Read PDF content as bytes
  pdf_bytes = file_obj.read()
  poller = document_analysis_client.begin_analyze_document("prebuilt-invoice", pdf_bytes)
 else:
  st.error("Unsupported file format. Please upload an image (JPEG/PNG) or PDF.")
  return None
 
 invoices = poller.result()
 return invoices

def save_to_csv(data, filename="extracted_invoices.csv"):
  """Saves extracted invoice data to a CSV file."""
  df = pd.DataFrame(data)
  try:
    df.to_csv(filename, index=False)
    st.success(f"Invoice data saved to {filename}")
  except Exception as e:
    st.error(f"Error saving data to CSV: {e}")

st.title("Document Analysis with Azure Form Recognizer")

uploaded_file = st.file_uploader("Choose an Image or PDF", type=["jpg", "png", "pdf"])

if uploaded_file is not None:
 invoices = analyze_document(uploaded_file)
 
 if invoices:
  data = []
  for idx, invoice in enumerate(invoices.documents):
   vendor_name = invoice.fields.get("VendorName")
   vendor_address = invoice.fields.get("VendorAddress")
   vendor_address_recipient = invoice.fields.get("VendorAddressRecipient")
   customer_name = invoice.fields.get("CustomerName")
   customer_id = invoice.fields.get("CustomerId")
   customer_address = invoice.fields.get("CustomerAddress")
   customer_address_recipient = invoice.fields.get("CustomerAddressRecipient")
   invoice_id = invoice.fields.get("InvoiceId")
   invoice_date = invoice.fields.get("InvoiceDate")
   invoice_total = invoice.fields.get("InvoiceTotal")
   due_date = invoice.fields.get("DueDate")
   purchase_order = invoice.fields.get("PurchaseOrder")
   billing_address_recipient = invoice.fields.get("BillingAddressRecipient")
   vendor_address_recipient = invoice.fields.get("VendorAddressRecipient")
   invoice_id = invoice.fields.get("InvoiceId")
   billing_address = invoice.fields.get("BillingAddress")
   shipping_address = invoice.fields.get("ShippingAddress")
   shipping_address_recipient = invoice.fields.get("ShippingAddressRecipient")
   data.append({
       "Invoice Number": idx + 1,
       "Vendor Name": vendor_name.value if vendor_name else None,
       "Vendor Address": vendor_address.value if vendor_address else None,
       "Vendor Address Recipient":vendor_address_recipient.value if vendor_address_recipient else None,
       "Customer Name": customer_name.value if customer_name else None,
       "Customer Id": customer_id.value if customer_id else None,
       "Invoice Id": invoice_id.value if invoice_id else None,
       "Customer Address": customer_address.value if customer_address else None,
       "Customer Address Recipient": customer_address_recipient.value if customer_address_recipient else None,
       "Invoice Id": invoice_id.value if invoice_id else None,
       "Invoice Date": invoice_date.value if invoice_date else None,
       "Invoice Total": invoice_total.value if invoice_total else None,
       "Due Date": due_date.value if due_date else None,
       "Purchase Order": purchase_order.value if purchase_order else None,
       "Billing Address": billing_address.value if billing_address else None,
       "Billing Address Recipient": billing_address_recipient.value if billing_address_recipient else None,
       "Shipping Address": shipping_address.value if shipping_address else None,
       "Shipping Address Recipient": shipping_address_recipient.value if shipping_address_recipient else None,
       
   })

  df = pd.DataFrame(data)
  transposed_df = df.T
  st.subheader("Extracted Invoice Data")
  st.dataframe(transposed_df, width=2500, height=600)

  #st.write(transposed_df)

  # Add button to trigger download
  if st.button("Download CSV"):
    save_to_csv(data)
 else:
    st.write("No invoices found in the document.")

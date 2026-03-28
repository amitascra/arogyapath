import frappe
import qrcode
from io import BytesIO
import base64

def generate_qr_code(data):
	"""Generate QR code and return base64 encoded image"""
	qr = qrcode.QRCode(version=1, box_size=10, border=5)
	qr.add_data(data)
	qr.make(fit=True)
	
	img = qr.make_image(fill_color="black", back_color="white")
	buffered = BytesIO()
	img.save(buffered, format="PNG")
	img_str = base64.b64encode(buffered.getvalue()).decode()
	return f"data:image/png;base64,{img_str}"

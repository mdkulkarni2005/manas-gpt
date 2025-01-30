import streamlit as st
import socket

# Digital Signature (Hidden)
AUTHOR_SIGNATURE = """
/*
* Created by: Manas D. Kulkarni
* Digital Signature: manas.d.kulkarni
* GitHub: https://github.com/mdkulkarni2005/manas-gpt
* Copyright © 2024 - All Rights Reserved
*/
"""

def verify_deployment():
    """Verify if the app is running locally or being hosted"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        is_local = local_ip.startswith(('127.', '192.168.', '10.', '172.'))

        if not is_local:
            st.error("⚠️ UNAUTHORIZED HOSTING DETECTED!")
            st.warning("""
            This application is designed for local use only.
            Original Creator: Manas D. Kulkarni
            GitHub: https://github.com/mdkulkarni2005/manas-gpt

            Please respect the creator's rights and run locally only.
            """)
            st.stop()
    except Exception:
        pass

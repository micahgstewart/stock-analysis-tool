from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='127.0.0.1',  # Local host
        port=8050,         # Port number
    ) 
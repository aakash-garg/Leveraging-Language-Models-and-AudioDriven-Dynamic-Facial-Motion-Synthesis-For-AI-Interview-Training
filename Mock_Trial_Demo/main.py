from website import create_app


app = create_app()
# ngrok.set_auth_token("28OY9NZ3lqIE48CG82AodpOOigX_4Lp5vtCix6WpBKkhnZdRf")
# run_with_ngrok(app)
if __name__ == '__main__':
    print('---Running Server---')
    app.run(debug=True)

    # app.run()

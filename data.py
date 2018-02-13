def Articles():
    # # create cursor
    #     cur = mysql.connection.cursor()

    #     # execute query
    #     cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

    #     # commit to DB
    #     mysql.connection.commit()

    #     # close connection
    #     cur.close()
    articles = [
        {
            'id': 1,
            'title': 'Aritcle One',
            'Author': 'Brad Traversy',
            'create_date': '04-25-2017'
        },
        {
            'id': 2,
            'title': 'Aritcle Two',
            'Author': 'John Doe',
            'create_date': '04-25-2017'
        },
        {
            'id': 3,
            'title': 'Aritcle Three',
            'Author': 'Brad Traversy',
            'create_date': '04-25-2017'
        }
    ]

    return articles

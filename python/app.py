import mysql.connector
import pandas as pd
from numpy import nan
from mysql.connector import Error
from mysql.connector import errorcode
from flask import Flask, render_template, request, url_for


app = Flask(__name__, static_url_path='/static')

class App:
    def __init__(self):
        self.rconnected = False
        self.nconnected = False
        self.check = False
        self.config = {}

        self.TABLES = {}
        self.pdata = ""
        self.ratings_data = ""
        self.links_data = ""
        self.tags_data = ""

    def set_config(self):
        self.config = {'host': 'mysql',
                       'port': 3306,
                       'r_user': 'root',
                       'r_pwd': '123',
                       'user':'newuser',
                       'password': '777',
                       'database': 'testdb'
                      }
                      
    def get_csv_data(self):
        self.pdata = pd.read_csv(r"./movies.csv", index_col=False, delimiter=',')
        #self.pdata = pd.read_csv(r"C:\Users\jlee0\Desktop\COMP0022\python\movies.csv", index_col=False, delimiter=',')
        self.pdata.fillna(0)
        self.pdata.head()

        self.ratings_data = pd.read_csv(r"./ratings.csv", index_col=False, delimiter=',')
        self.ratings_data.fillna(0)
        self.ratings_data.head()
        
        self.links_data = pd.read_csv(r"./links.csv", index_col=False, delimiter=',')
        self.links_data.fillna(0,inplace=True)
        self.links_data.head()
        
        self.tags_data = pd.read_csv(r"./tags.csv", index_col=False, delimiter=',')
        self.tags_data.fillna(0,inplace=True)
        self.tags_data.head()

    def connect_with_root(self):
        db_host = self.config.get('host')
        db_port = self.config.get('port')
        db_name = self.config.get('database')
        db_ruser = self.config.get('r_user')
        db_rpwd = self.config.get('r_pwd')
        self.cnx = mysql.connector.connect(user=db_ruser, password=db_rpwd, host=db_host, port=db_port, database=db_name)
        db_Info = self.cnx.get_server_info()
        print("connected to mysql", db_Info)
        self.rconnected = True

    def grant_prev(self):
        if self.rconnected != True:
            print("please make a connection first")
            exit()
        else:
            cursor = self.cnx.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS movies;")
            cursor.execute("GRANT ALL PRIVILEGES ON movies.* to 'newuser'@'%';")
            cursor.execute("SET global group_concat_max_len = 15000000;")
            cursor.execute("SET global max_allowed_packet = 1073741824;")
            cursor.execute("SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'STRICT_TRANS_TABLES',''));")
            cursor.close()
    
    def close_connec_root(self):
        if self.rconnected != False:
            self.cnx.close()
            self.rconnected = False
        else:
            print("connection is already closed")
        
    def connect_newuser(self, db_name):
        db_user = self.config.get('user')
        db_pwd = self.config.get('password')
        db_host = self.config.get('host')
        db_port = self.config.get('port')
        self.cnx2 = mysql.connector.connect(user=db_user, password=db_pwd, host=db_host, port=db_port, database=db_name)
        self.nconnected = True
    
    def create_table_with_data(self):
        cursor = self.cnx2.cursor()
        if not self.check:
            return 0
        else:
            # Create SQL for creating tables
            cursor.execute("DROP TABLE IF EXISTS movies_data;")
            cursor.execute("DROP TABLE IF EXISTS movies_ratings;")
            cursor.execute("DROP TABLE IF EXISTS movies_links;")
            cursor.execute("DROP TABLE IF EXISTS movies_tags;")
          

            self.TABLES['movies_data'] = (
                "CREATE TABLE movies_data ("
                "  movie_ID INT NOT NULL AUTO_INCREMENT,"
                "  title VARCHAR(255) NOT NULL,"
                "  genre VARCHAR(255) NOT NULL,"
                "  content VARCHAR(255) NOT NULL,"
                "  director VARCHAR(255) NOT NULL,"
                "  lead_actor VARCHAR(255) NOT NULL,"
                "  rotten_tomatoes VARCHAR(255) NOT NULL,"
                "  rating VARCHAR(255) NOT NULL,"
                "  tags VARCHAR(2000) NOT NULL,"
                "  PRIMARY KEY(movie_ID));"
            )
            self.TABLES['movies_ratings'] = (
                "CREATE TABLE movies_ratings ("
                "  user_ID INT NOT NULL,"
                "  movie_ID INT NOT NULL,"
                "  rating VARCHAR(255) NOT NULL,"
                "  timestamp VARCHAR(255) NOT NULL,"
                "  PRIMARY KEY(user_ID, movie_ID));"
            )
            self.TABLES['movies_links'] = (
                "CREATE TABLE movies_links ("
                "  movie_ID INT NOT NULL,"
                "  imdbId VARCHAR(255) NOT NULL,"
                "  tmdbId VARCHAR(255) NOT NULL,"
                "  PRIMARY KEY(movie_ID));"
            )
            self.TABLES['movies_tags'] = (
                "CREATE TABLE movies_tags ("
                "  user_ID INT NOT NULL,"
                "  movie_ID INT NOT NULL,"
                "  tag VARCHAR(255) NOT NULL,"
                "  timestamp VARCHAR(255) NOT NULL,"
                "  PRIMARY KEY(user_ID, movie_ID, tag));"
            )

            for table_name in self.TABLES:
                table_description = self.TABLES[table_name]
                try:
                    print("Creating table {}: ".format(table_name), end='', flush=True)
                    cursor.execute(table_description)
                except mysql.connector.Error as err:
                    if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                        print("already exists.", flush=True)
                    else:
                        print(err.msg, flush=True)
                else:
                    print("OK", flush=True)
            
            #format pdata
            if len(self.pdata.columns.tolist()) < 9:
                self.pdata = self.pdata.reindex(self.pdata.columns.tolist() + ['rating', 'tags'], axis=1, fill_value="N/A")
                self.pdata.fillna("N/A")
            else:
                pass
            
            cursor.execute("SET autocommit = 0;")
            cursor.execute("START TRANSACTION;")
            #Populate tables
            for i, row in self.pdata.iterrows():
                row = row.fillna(0)
                if i == 0:
                    print("INSERTING RECORDS", flush=True)
                sql = "INSERT INTO movies.movies_data VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, tuple(row))

            
            for i, row in self.ratings_data.iterrows():
                if i == 0:
                    print("INSERTING RECORDS", flush=True)
                sql = "INSERT INTO movies.movies_ratings VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, tuple(row))


            for i, row in self.links_data.iterrows():
                if i == 0:
                    print("INSERTING RECORDS", flush=True)
                sql = "INSERT INTO movies.movies_links VALUES (%s, %s, %s)"
                cursor.execute(sql, tuple(row))

                
            for i, row in self.tags_data.iterrows():
                if i == 0:
                    print("INSERTING RECORDS", flush=True)
                sql = "INSERT INTO movies.movies_tags VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, tuple(row))
            cursor.execute("COMMIT;")

            cursor.close()

    def get_unique_genres(self):
        """
        Extracts all the possible genres in the movies database
        """
        
        cursor = self.cnx2.cursor()
        cursor.execute("SELECT genre FROM movies.movies_data;")
        genres_column = cursor.fetchall()
        unique_genres = {}

        for row in genres_column:
            for genre in str(row[0]).split(sep='|'):
                unique_genres[genre] = None

        print(f"All possible genres: {list(unique_genres.keys())}", flush=True)
        cursor.close()
        return list(unique_genres.keys())

    def use_case_1(self, filters):
        cursor = self.cnx2.cursor()
        query_params = ''
        base_query = 'SELECT * FROM movies.movies_data'

        print(f"Filters: {filters}", flush=True)

        if filters is None:
            # This condition is activated through a GET request on the page
            query_params = ' LIMIT 20 OFFSET 20;'
        else:
            # Additional query parameters found from filters argument - build SQL command
            filters = filters.to_dict(flat=False)

            print(f"Form filters: {filters}", flush=True)

            if "genre" in filters.keys():
                selected_genre = filters["genre"][0]
                print(f"Selected genre: {selected_genre}", flush=True)
                if selected_genre == "none":
                    print("0")
                    pass
                else:
                    query_params += f" WHERE genre LIKE '%{selected_genre}%'"
                del filters["genre"]

            if len(filters) != 0:
                query_params += ' ORDER BY'

                # Dynamically add sorting filters to query
                for idx, (col_name, col_filter) in enumerate(filters.items()):
                    query_params += f' {col_name} {str(col_filter[0]).upper()}'
                    if idx < len(filters.items()) -1 and len(filters.items()) > 1:
                        query_params += ','
            query_params += ' LIMIT 20 OFFSET 20;'
        
        # Build final query for execution
        base_query += query_params
        print(f'USE CASE 1 FINAL QUERY: "{base_query}"', flush=True)

        cursor.execute(base_query)
        result = cursor.fetchall() 
        cursor.close()
        return result
    
    def print_first_10_ratings(self):
        cursor = self.cnx2.cursor()
        cursor.execute("SELECT * FROM movies.movies_ratings WHERE movie_ID < 10;")
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def print_first_10_tags(self):
        cursor = self.cnx2.cursor()
        cursor.execute("SELECT * FROM movies.movies_tags WHERE movie_ID < 10;")
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def print_first_10_links(self):
        cursor = self.cnx2.cursor()
        cursor.execute("SELECT * FROM movies.movies_links WHERE movie_ID < 10;")
        result = cursor.fetchall()
        cursor.close()
        return result

    def close_nconnect(self):
        self.cnx2.close()

    def search_movie(self, movie):
        cursor = self.cnx2.cursor()
        cursor.execute("SELECT * FROM movies.movies_data WHERE title LIKE" + "'%" + movie + "%';")
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_movie_info(self):
        try:
            self.connect_with_root()
            cursor = self.cnx.cursor()
            cursor.execute("SELECT * FROM movies.movies_data LIMIT 1;")
            result = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM movies.movies_data;")
            result2 = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'movies' AND table_name = 'movies_data';")
            count = cursor.fetchall()[0][0]
            cursor.close()
            self.close_connec_root()
            if result != []:
                if int(result2[0][0]) == 9742:
                    self.check = False
                    if count < 9:
                        self.check = True
                        pass
                    else:
                        return 0
                else:
                    self.check = True
                    pass
            else:
                self.check = True
                pass
        except:
            self.check = True
            pass         
        rdata = pd.read_csv(r"./RTmovies.csv", index_col=False, delimiter=',')
        #rdata = pd.read_csv(r"C:\Users\jlee0\Desktop\COMP0022\python\RTmovies.csv", index_col=False, delimiter=',')
        rdata.fillna(0)
        rdata.head()
        titles = rdata['movie_title'].tolist()
        dbtitles = self.pdata['title'].tolist()
        self.pdata = self.pdata.reindex(self.pdata.columns.tolist() + ['content', 'director', 'lead_actors', 'rotten_tomato'], fill_value=0, axis=1)
        count = 0
        for title in dbtitles:
            ntitle = title[:title.rfind('(')][:-1]
            if ntitle in titles:
                idx = titles.index(ntitle)
                data = rdata.iloc[idx]
                w, x, y, z1, z2 = data['content_rating'], data['directors'], data['actors'], data['tomatometer_rating'], data['audience_rating']
                try:
                    y = y.split(',')[0] + ", " + y.split(',')[1]
                except IndexError:
                    y = y.split(',')[0]
                except AttributeError:
                    y = 0
                score = str(z1).split('.')[0] + '%, ' + str(z2).split('.')[0] + '%'
                self.pdata.loc[self.pdata['title'] == title, 'content'] = w
                self.pdata.loc[self.pdata['title'] == title, 'director'] = x
                self.pdata.loc[self.pdata['title'] == title, 'lead_actors'] = y
                self.pdata.loc[self.pdata['title'] == title, 'rotten_tomato'] = score
            else:
                self.pdata.loc[self.pdata['title'] == title, 'content'] = "N/A"
                self.pdata.loc[self.pdata['title'] == title, 'director'] = "N/A"
                self.pdata.loc[self.pdata['title'] == title, 'lead_actors'] = "N/A"
                self.pdata.loc[self.pdata['title'] == title, 'rotten_tomato'] = "N/A"

    def fill_rating(self):
        cursor = self.cnx2.cursor()
        cursor.execute("SELECT rating FROM movies_data WHERE movie_ID = 1;")
        result = cursor.fetchone()[0]
        if result != "N/A":
            pass
        else:
            cursor.execute("""UPDATE movies_data m
                              INNER JOIN (SELECT movies_data.movie_Id, ROUND(AVG(movies_ratings.rating), 2) as rating 
                              FROM movies_ratings, movies_data WHERE movies_data.movie_Id = movies_ratings.movie_Id
                              GROUP BY movies_ratings.movie_Id) r
                              ON m.movie_Id = r.movie_Id
                              SET m.rating = r.rating;""")
            self.cnx2.commit()
        cursor.close()

    def fill_tags(self):
        cursor = self.cnx2.cursor()
        cursor.execute("SELECT tags FROM movies_data WHERE movie_ID = 1;")
        result = cursor.fetchone()[0]
        if result != "N/A":
            pass
        else:
            cursor.execute("""UPDATE movies_data m INNER JOIN (
                              SELECT movies_data.movie_Id, GROUP_CONCAT(DISTINCT tag) as tags
                              FROM movies_tags, movies_data WHERE movies_data.movie_Id = movies_tags.movie_Id
                              GROUP BY movies_tags.movie_Id) r
                              ON m.movie_Id = r.movie_Id
                              SET m.tags = r.tags;""")
            self.cnx2.commit()
        cursor.close()
        
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/use_case_1", methods=['GET', 'POST'])
def get_data():
    app1 = App()
    app1.set_config()
    app1.get_csv_data()
    app1.get_movie_info()
    try:
        app1.connect_with_root()
    except Error as e:
        print("Error while connecting: ", e, flush=True)
    if app1.rconnected != False:
        app1.grant_prev()
        app1.close_connec_root()
    try:
        app1.connect_newuser("movies")
    except Error as e:
        print("Error while connecting: ", e, flush=True)    
    if app1.nconnected != False:
        app1.create_table_with_data()
        app1.fill_rating()
        app1.fill_tags()
    
    # Load table column names template
    headings_display = ['Movie ID', 'Title', 'Genre(s)', 'Content', 'Director',
        'Lead Actor', 'Rating (Rotten Tomatoes)', 'Rating (Overall)', 'Tags']

    # Fetch unique genres of the table to populate selection button in UI
    unique_genres = app1.get_unique_genres()

    # POST button events
    if request.method == "POST":
        # Pass the POST form filter data to execute query
        query_result = app1.use_case_1(filters=request.form)
    else:
        # Fetch query result
        query_result = app1.use_case_1(filters=None)

    return render_template(
        'use_case_1.html',
        query_res=query_result,
        len=len(headings_display),
        unique_genres=unique_genres,
        headings_display=headings_display
    )

@app.route("/view_ratings")
def get_ratings():
    app1 = App()
    app1.set_config()
    app1.get_csv_data()
    try:
        app1.connect_with_root()
    except Error as e:
        print("Error while connecting: ", e)
    if app1.rconnected != False:
        app1.grant_prev()
        app1.close_connec_root()
    try:
        app1.connect_newuser("movies")
    except Error as e:
        print("Error while connecting: ", e)    
    if app1.nconnected != False:
        app1.create_table_with_data()
        #something = app1.print_first_10()
        #app1.close_nconnect()
    return render_template("view_ratings.html", data=app1.print_first_10_ratings())

@app.route("/view_links")
def get_links():
    app1 = App()
    app1.set_config()
    app1.get_csv_data()
    try:
        app1.connect_with_root()
    except Error as e:
        print("Error while connecting: ", e)
    if app1.rconnected != False:
        app1.grant_prev()
        app1.close_connec_root()
    try:
        app1.connect_newuser("movies")
    except Error as e:
        print("Error while connecting: ", e)    
    if app1.nconnected != False:
        app1.create_table_with_data()
        #something = app1.print_first_10()
        #app1.close_nconnect()
    return render_template("view_links.html", data=app1.print_first_10_links())

@app.route("/view_tags")
def get_tags():
    app1 = App()
    app1.set_config()
    app1.get_csv_data()
    try:
        app1.connect_with_root()
    except Error as e:
        print("Error while connecting: ", e)
    if app1.rconnected != False:
        app1.grant_prev()
        app1.close_connec_root()
    try:
        app1.connect_newuser("movies")
    except Error as e:
        print("Error while connecting: ", e)    
    if app1.nconnected != False:
        app1.create_table_with_data()
        #something = app1.print_first_10()
        #app1.close_nconnect()
    return render_template("view_tags.html", data=app1.print_first_10_tags())

@app.route("/search",  methods=["GET", "POST"])
def search():
    return render_template("search.html")

@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "GET":
        return f"The URL was accessed directly. Try going to '/search'"
    if request.method == "POST":
        result = request.form.get("search")
        app1 = App()
        app1.set_config()
        app1.get_csv_data()
        try:
            app1.connect_with_root()
        except Error as e:
            print("Error while connecting: ", e)
        if app1.rconnected != False:
            app1.grant_prev()
            app1.close_connec_root()
        try:
            app1.connect_newuser("movies")
        except Error as e:
            print("Error while connecting: ", e)    
        if app1.nconnected != False:
            movied = app1.search_movie(result)
        if movied != []:
            return render_template("result.html", result=movied)
        else:
            return render_template("result.html", result="No results found")

if __name__ == "__main__":
    app.run(debug=True)
    #app1 = App()
    #app1.set_config()
    #app1.get_csv_data()
    #app1.get_movie_info()






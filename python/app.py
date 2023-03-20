import mysql.connector
import pandas as pd
import numpy as np
import itertools
from numpy import nan
from mysql.connector import Error
from mysql.connector import errorcode
from flask import Flask, render_template, request, url_for
from sklearn.preprocessing import LabelEncoder
from operator import methodcaller
from scipy.stats import pearsonr, spearmanr


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
    
    # ESSENTIAL FUNCTIONS FOR BUILDING DATABASE
    # Create tables and populate the tables with CSV data
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
    
    
    # USE CASE 1 FUNCTIONS
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
        return sorted(list(unique_genres.keys()))
    
    def build_date_query(self, filters) -> str:
        query_params = ' CAST(SUBSTRING(title, -5, 4) AS SIGNED)'
        year_before, year_after = filters["year_before"][0], filters["year_after"][0]

        # No filters for years - we skip adding date to our query
        if year_before == '' and year_after == '':
            year_before, year_after = 9999, 0
            query_params += f" BETWEEN {year_after} AND {year_before}"
    
        # Both filters for years are selected
        elif year_before != '' and year_after != '':
            # 2 years are specified, so we need to check if before < after
            query_params += f" {'NOT' if year_before < year_after else ''} BETWEEN {year_after} AND {year_before} "
        else:
            year_before = year_before if year_before != '' else 9999
            year_after = year_after if year_after != '' else 0
            query_params += f" BETWEEN {year_after} AND {year_before} "

        return query_params

    def use_case_1(self, filters):
        """
        Our solution to USE CASE 1 is to build a flexible SQL query. The final query is built depending on the user's
        inputs to the associated radio buttons in use_case_1.html, where the 'name' attribute of the radio button is 
        the required column name in our movies.movies_data table, and the 'value' attribute of the radio button 
        corresponds to the sorting order that the user wants. The 'name' and 'value' attribute of every activated radio
        button is passed into this function via the 'filters' argument.

        E.g. If the user selects the "rating" radio button and ascending sorting order, then the 'filters' object should 
        contain something like: {'rating': ['asc']}.

        You can select multiple of these filters in the filter form.
        """

        cursor = self.cnx2.cursor()
        query_params = ''
        base_query = 'SELECT * FROM movies.movies_data'

        if filters is None:     # This condition is activated when a GET request is issued for the webpage
            pass
        else:                   # The function has received more than 0 filters - we shall process these additional filters
            filters = filters.to_dict(flat=False)
            print(f"Filters: {filters}", flush=True)

            # NOTE: The 'genre' filter uses a WHERE clause to get movies with the selected genre, hence
            # has higher priority than the ORDER BY filters for the radio buttons.
            if any(column in filters.keys() and filters[column][0] != '' for column in ["genre", "year_before", "year_after"]):
                query_params += ' WHERE '

                if "genre" in filters.keys():
                    selected_genre = filters["genre"][0]
                    query_params += f"genre LIKE '%{selected_genre}%' AND " if selected_genre != "" else ''
                date_query = self.build_date_query(filters)
                query_params += date_query if date_query != '' else ''
            
            # Select and text boxes must return at least an empty string '' as its value, so these fields will always
            # be populated. Therefore, we need to delete these from the filters dictionary before proceeding.
            del filters["genre"], filters["year_before"], filters['year_after']
            
            if len(filters) != 0:
                query_params += ' ORDER BY'

                # Dynamically add sorting filters to query
                for idx, (col_name, col_filter) in enumerate(filters.items()):
                    query_params += f' {col_name} {str(col_filter[0]).upper()}'
                    if idx < len(filters.items()) -1 and len(filters.items()) > 1:
                        query_params += ','
        
        # Add paginator
        query_params += ' LIMIT 20 OFFSET 20;'

        # Build final query for execution
        base_query += query_params
        print(f'USE CASE 1 FINAL QUERY: "{base_query}"', flush=True)

        cursor.execute(base_query)
        result = cursor.fetchall() 
        print(f'UC1 Results: {result}', flush=True)
        cursor.close()
        return result

    # USE CASE 2 FUNCTIONS
    def use_case_2(self, filters):
        cursor = self.cnx2.cursor()
        query_params = ''
        base_query = "SELECT * FROM movies.movies_data"

        if filters is None:     # This condition is activated when a GET request is issued for the webpage
            query_params = ' LIMIT 20 OFFSET 20;'
        else:
            filters = filters.to_dict(flat=False)
            print(f"Filters: {filters}", flush=True)

            if 'search' in filters.keys():
                movie_title = filters['search'][0]
                query_params += f" WHERE title LIKE '%{movie_title}%'"

        # Add paginator
        # query_params += ' LIMIT 20 OFFSET 20;'
        base_query += query_params + ';'
        print(f'USE CASE 2 FINAL QUERY: "{base_query}"', flush=True)

        cursor.execute(base_query)
        result = cursor.fetchall()
        print(result)
        cursor.close()
        return result


    # USE CASE 3 FUNCTIONS
    def get_user_rating_correlation(self, query_result):
        """
        Calculates the correlation coefficients between user rating for a specific movie title and user 
        average rating

        @params query_result: A SQL result consisting of 3 columns: User ID, User rating for a specific
            film & User rating history (average rating for all reviews)
        """
        user_ratings = [float(row[1]) for row in query_result]      # row[1] corresponds to the user rating
        user_av_ratings = [row[2] for row in query_result]          # row[2] corresopnds to the user average rating
        correlation_coefficient = np.corrcoef(user_ratings, user_av_ratings)[0][1]
        return correlation_coefficient

    def uc3_prepare_data_for_plot(self, query_results):
        """
        Processes the query results for use case 3 such that it is compatible for plotting using Chart.js.
        This includes updating labels (column 0), and combining rating data colummns into (x,y) pairs for
        plotting.

        @params query_result: A SQL result consisting of 3 columns: User ID, User rating for a specific
            film & User rating history (average rating for all reviews)
        """

        labels, data = [], []

        for row in query_results:
            labels.append(f'User ID: {row[0]}')         # Add label to user id for visualisation in Chart.js
            data.append({'x': row[1], 'y': row[2]})     # Combine rating data columns into x,y pairs for plotting

        return labels, data

    def use_case_3(self, filters):
        cursor = self.cnx2.cursor()

        if filters is None:     # This condition is activated when a GET request is issued for the webpage
            return None
        else:                   # This condition is activated if 
            filters = filters.to_dict(flat=False)
            # print(f"Filters: {filters}", flush=True)
            
            base_query = ''
            context = dict.fromkeys(['message', 'query_result', 'correlation', 'movie_title', 'unique_genres'])

            movie_title = filters['movie_title_field'][0]
            selected_subcase = filters['selected_subcase'][0]
            genre_filter = filters['genre'][0]
            # print(f'genre filter: {genre_filter}', flush=True)

            if selected_subcase == 'subcase1':
                # We need to pass an error message if the user selects a genre for case 1!
                if genre_filter != '' or movie_title == '':
                    context['message'] = 'Unexpected filters for case 1. Check your movie and genre filters again!'
                    return context
                else:
                    result = None
                    # print('use case 3 subcase 1', flush=True)
                    try:
                        base_query = f"""
                            SELECT A.user_ID, A.rating, B.av 
                                FROM (
                                    SELECT * 
                                    FROM movies.movies_ratings
                                    WHERE movie_ID = (
                                        SELECT movie_ID 
                                        FROM movies.movies_data
                                        WHERE title LIKE '%{movie_title}%'
                                    )
                                ) A LEFT JOIN 
                                (
                                    SELECT user_ID, AVG(rating) AS av
                                    FROM movies.movies_ratings
                                    GROUP BY user_ID
                                ) B ON A.user_ID = B.user_ID;
                        """
                        cursor.execute(base_query) 
                        result = cursor.fetchall()
                        cursor.close()
                        correlation = self.get_user_rating_correlation(result)
                        processed_labels, processed_data = self.uc3_prepare_data_for_plot(result)
                        
                        # print(f"result: {result}", flush=True)
                        # print(f"data correlation: {correlation}", flush=True)
                        # print(f"processed labels: {processed_labels}", flush=True)
                        # print(f"processed data: {processed_data}", flush=True)

                        context["message"] = 'Completed analysis for Subcase 1!'
                        context["movie_title"] = movie_title
                        context["labels"] = processed_labels
                        context["query_res"] = processed_data
                        context["correlation"] = correlation
                    except mysql.connector.errors.DataError:
                        context["message"] = f'There are multiple movie titles for "{movie_title}" that you entered. Please enter the exact movie title.'
                   
                    return context        
            
            elif selected_subcase == 'subcase2':
                if genre_filter == '' or movie_title == '':
                    context['message'] = 'Unexpected filters for case 2. Check your movie and genre filters again!'
                    return context
                else:
                    result = None
                    # print('use case 3 subcase 2', flush=True)
                    try:
                    
                        # Query to get average user rating based on selected genre
                        base_query = f"""
                            SELECT C.user_ID, D.rating, C.av
                            FROM (
                                SELECT B.user_ID, AVG(B.rating) as av
                                FROM movies.movies_ratings AS B
                                INNER JOIN (
                                    SELECT movie_ID
                                    FROM movies.movies_data
                                    WHERE genre LIKE '%{genre_filter}%'
                                ) AS A
                                ON B.movie_ID = A.movie_ID
                                GROUP BY B.user_ID
                            ) AS C
                            INNER JOIN (
                                SELECT user_ID, rating
                                FROM movies.movies_ratings
                                WHERE movie_ID = (
                                    SELECT movie_ID 
                                    FROM movies.movies_data
                                    WHERE title LIKE '%{movie_title}%'
                                )
                            ) AS D
                            ON C.user_ID = D.user_ID
                        """

                        # print(base_query, flush=True)
                        cursor.execute(base_query)
                        result = cursor.fetchall()
                        # print(f"Subcase 2 results: {result}", flush=True)

                        cursor.close()

                        correlation = self.get_user_rating_correlation(result)
                        processed_labels, processed_data = self.uc3_prepare_data_for_plot(result)
                        
                        # print(f"result: {result}", flush=True)
                        # print(f"data correlation: {correlation}", flush=True)
                        # print(f"processed labels: {processed_labels}", flush=True)
                        # print(f"processed data: {processed_data}", flush=True)

                        context["message"] = 'Completed analysis for Subcase 2!'
                        context["movie_title"] = movie_title
                        context["labels"] = processed_labels
                        context["query_res"] = processed_data
                        context["correlation"] = correlation
                    except mysql.connector.errors.DataError:
                        context["message"] = f'There are multiple movie titles for "{movie_title}" that you entered. Please enter the exact movie title.'
                    return context       
            
    #USE CASE 4 FUNCTION
    def use_case_4(self):
        base_query = ''
        context = dict.fromkeys(['user', 'all_data', 'result'])
        cursor = self.cnx2.cursor()
        cursor.execute("""SELECT mt.user_ID, mt.movie_ID, 
                          GROUP_CONCAT(mt.tag) as tag,
                          GROUP_CONCAT(DISTINCT md.genre) as genres,
                          GROUP_CONCAT(DISTINCT md.rating) as rating
                          FROM movies_tags mt
                          INNER JOIN movies_data md ON mt.movie_ID = md.movie_ID
                          GROUP BY mt.user_ID, mt.movie_ID;""")
        result = cursor.fetchall()
        cursor.execute("""SELECT mt.tag, GROUP_CONCAT(movies_data.title) as title, GROUP_CONCAT(movies_data.genre) as genre
                          FROM movies_tags mt
                          INNER JOIN movies_data ON mt.movie_Id = movies_data.movie_Id
                          GROUP BY mt.tag;""")
        c_result = cursor.fetchall()
        idx = ["user_id", "movie_id", "tags", "genres", "rating"]
        result = pd.DataFrame(result, columns=idx)
        result['genres'] = result['genres'].str.split('|')
        result['genres'] = result['genres'].apply(lambda x: ", ".join(x))
        result['tags'] = result['tags'].apply(lambda x: x.lower())
        tag_LE = LabelEncoder()
        genre_LE = LabelEncoder()
        all_tags = ",".join(result['tags'])
        all_genres = ",".join(result['genres'])
        unique_tags = list(set(all_tags.split(",")))
        unique_genres = list(set(all_genres.split(",")))
        tag_LE.fit(unique_tags)
        genre_LE.fit(unique_genres)
        def encode_tags(tags):
            return [tag_LE.transform([tag])[0] for tag in tags.split(",")]
        def encode_genres(genres):
            return [genre_LE.transform([genre])[0] for genre in genres.split(",")]
        result['encoded_tags'] = result['tags'].apply(encode_tags)
        result['encoded_genres'] = result['genres'].apply(encode_genres)
        result['rating'] = result['rating'].fillna(0)
        for idx in result.index[result['rating'] == "N/A"].tolist():
            result.loc[idx, 'rating'] = 0
        result['rating'] = result['rating'].apply(lambda x: float(x))
        g_corr_list, r_corr_list = [], []
        for user_id in result['user_id'].unique():
            user_data = result[(result['user_id'] == user_id)]

            encoded_tags = user_data['encoded_tags'].values.tolist()
            encoded_genres = user_data['encoded_genres'].values.tolist()
            ratings = user_data['rating'].values.tolist()
            flat_tags = np.array([tag for tags in encoded_tags for tag in tags])
            flat_genres = np.array([genre for genres in encoded_genres for genre in genres])

            if len(flat_genres) < 2:
                flat_genres = np.append(flat_genres, 0)
            if len(flat_tags) < 2:
                flat_tags = np.append(flat_tags, 0)
            if len(ratings) < 2:
                ratings = np.append(ratings, 0)

            if len(flat_tags) > len(flat_genres):
                flat_genres = np.pad(flat_genres, (0, len(flat_tags) - len(flat_genres)), 'constant')
            elif len(flat_genres) > len(flat_tags):
                flat_tags = np.pad(flat_tags, (0, len(flat_genres) - len(flat_tags)), 'constant')
            else:
                pass
            
            if len(flat_tags) > len(ratings):
                ratings = np.pad(ratings, (0, len(flat_tags) - len(ratings)), 'constant')
            elif len(ratings) > len(flat_tags):
                flat_tags = np.pad(flat_tags, (0, len(ratings) - len(flat_tags)), 'constant')
            else:
                pass
            
            
            g_corr, _ = pearsonr(flat_tags, flat_genres)
            r_corr, _ = pearsonr(flat_tags, ratings)
            if pd.isna(r_corr):
                r_corr = 0.0

            g_corr_list.append(g_corr)
            r_corr_list.append(r_corr) 
        
        glabels, gdata = [], []

        for y, x in zip(g_corr_list, result['user_id'].unique().tolist()):
            glabels.append(f'User ID: {x}')         # Add label to user id for visualisation in Chart.js
            gdata.append({'x': x, 'y': y})     # Combine rating data columns into x,y pairs for plotting
        
        rlabels, rdata = [], []
        for y, x in zip(r_corr_list, result['user_id'].unique().tolist()):
            rlabels.append(f'User ID: {x}')         # Add label to user id for visualisation in Chart.js
            rdata.append({'x': x, 'y': y})

        labels = [glabels, rlabels]
        data = [gdata, rdata]
        all_data = dict.fromkeys(['rlabels', 'rdata', 'glabels', 'gdata'])
        all_data['rlabels'] = rlabels
        all_data['rdata'] = rdata
        all_data['glabels'] = glabels
        all_data['gdata'] = gdata
        context['user'] = result['user_id'].unique().tolist()
        context['all_data'] = all_data
        context['result'] = c_result
        return context

    
    def predict_aggregate_ratings(self, ratings_data):
        """
        We use the least squares method for making predictions.
        """

        ratings_data = [(row[0], float(row[1])) for row in ratings_data]
        ratings_data = np.array(ratings_data)

        X = ratings_data[:, 0]      # user ids
        y = ratings_data[:, 1]      # user ratings

        # List to store predictions of aggregate ratings of different preview sizes
        preview_size_labels = []
        actual_aggregate_ratings = []
        predicted_aggregate_ratings = []

        for preview_size in range(3, 20):
            preview_size_labels.append(preview_size)
            # Choose a small subset of ratings as the preview audience
            preview_indices = np.random.choice(len(X), size=preview_size, replace=False)
            preview_ratings = y[preview_indices]

            # Remove the preview audience from the training set
            X_train = np.delete(X, preview_indices)
            y_train = np.delete(y, preview_indices)

            # Compute coefficients of linear regression model
            A = np.vstack([X_train, np.ones(len(X_train))]).T
            coeffs, _, _, _ = np.linalg.lstsq(A, y_train, rcond=None)

            # Make predictions for overall rating
            X_all = np.unique(X)
            y_all_pred = np.dot(np.vstack([X_all, np.ones(len(X_all))]).T, coeffs)

            actual_aggregate_ratings.append(np.mean(y))
            predicted_aggregate_ratings.append(np.mean(y_all_pred))

        return preview_size_labels, actual_aggregate_ratings, predicted_aggregate_ratings


    # USE CASE 5 FUNCTIONS        
    def use_case_5(self, filters):
        cursor = self.cnx2.cursor()

        if filters is None:     # This condition is activated when a GET request is issued for the webpage
            return None
        else:
            base_query = ''
            context = dict.fromkeys(['message', 'movie_title', 'actual_av', 'predicted_av'])

            filters = filters.to_dict(flat=False)
            # print(f"Filters: {filters}", flush=True)
            
            if 'movie_title' in filters.keys():
                movie_title = filters['movie_title'][0]
            
                base_query = f"""
                    SELECT user_ID, rating 
                    FROM movies.movies_ratings
                    WHERE movie_ID = (
                        SELECT movie_ID
                        FROM movies.movies_data
                        WHERE title LIKE '%{movie_title}%'
                    )
                """

                # print(f'USE CASE 5 FINAL QUERY: "{base_query}"', flush=True)

                cursor.execute(base_query)
                result = cursor.fetchall()
                cursor.close()

                preview_size_labels, actual_av_ratings, predicted_av_ratings = self.predict_aggregate_ratings(result)

                context['preview_size_labels'] = preview_size_labels
                context['actual_av'] = actual_av_ratings
                context['predicted_av'] = predicted_av_ratings
                context['movie_title'] = movie_title
                context['message'] = f'Completed ratings prediction for {movie_title}'
                return context
            return None

    def print_first_10_links(self):
        cursor = self.cnx2.cursor()
        cursor.execute("SELECT * FROM movies.movies_links WHERE movie_ID < 10;")
        result = cursor.fetchall()
        cursor.close()
        return result

    def close_nconnect(self):
        self.cnx2.close()

    
        
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/render_use_case_1", methods=['GET', 'POST'])
def uc_1():
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
        retrieved_form_data = request.form
        query_result = app1.use_case_1(filters=retrieved_form_data)
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


@app.route("/render_use_case_2", methods=["GET", "POST"])
def uc_2():
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
    
    # Load table column names template
    headings_display = ['Movie ID', 'Title', 'Genre(s)', 'Content', 'Director',
        'Lead Actor', 'Rating (Rotten Tomatoes)', 'Rating (Overall)', 'Tags']
    
    if request.method == "POST":
        query_result = app1.use_case_2(filters=request.form)
    else:
        query_result = app1.use_case_2(filters=None)
    
    return render_template(
        'use_case_2.html',
        len=len(headings_display),
        query_res=query_result,
        headings_display=headings_display
    )
    
@app.route("/render_use_case_3", methods=["GET", "POST"])
def uc_3():
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

    headings_display = ['user_ID', 'movie_ID', 'rating', 'timestamp']

    # Fetch unique genres of the table to populate selection button in UI
    unique_genres = app1.get_unique_genres()

    if request.method == "POST":
        context = app1.use_case_3(filters=request.form)
    else:
        context = app1.use_case_3(filters=None)
    
    return render_template(
        'use_case_3.html',
        len=len(headings_display),
        context=context,
        unique_genres=unique_genres,
        headings_display=headings_display
    )

@app.route("/render_use_case_4", methods=["GET", "POST"])
def uc4():
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
    item = app1.use_case_4()
    heading = list(item.keys())
    l = len(heading)
    return render_template("use_case_4.html", result=item['result'], heading=heading, len=l, all_data=item['all_data'])

@app.route("/render_use_case_5", methods=["GET", "POST"])
def uc_5():
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
    
    if request.method == "POST":
        context = app1.use_case_5(filters=request.form)
    else:
        context = app1.use_case_5(filters=None)
    
    return render_template(
        'use_case_5.html',
        context=context,
    )
    

if __name__ == "__main__":
    app.run(debug=True)
    #app1 = App()
    #app1.set_config()
    #app1.get_csv_data()
    #app1.get_movie_info()
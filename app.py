from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

# PostgreSQL connection
conn = psycopg2.connect(
    os.environ["DATABASE_URL"]
)

cursor = conn.cursor()

# Create movies table
cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    genre TEXT,
    rating TEXT,
    status TEXT,
    image_url TEXT
)
""")

# Add columns if an older table already exists
cursor.execute("""
ALTER TABLE movies
ADD COLUMN IF NOT EXISTS image_url TEXT
""")

cursor.execute("""
ALTER TABLE movies
ADD COLUMN IF NOT EXISTS description TEXT
""")

cursor.execute("""
ALTER TABLE movies
ADD COLUMN IF NOT EXISTS watch_url TEXT
""")

conn.commit()


# ---------------- HOME / MOVIE LIST ----------------

@app.route("/")
def home():

    keyword = request.args.get("keyword", "")
    sort = request.args.get("sort", "title")
    genre = request.args.get("genre", "")

    search_value = "%" + keyword + "%"

    # Search + Genre + Sort

    if sort == "rating_high":

        cursor.execute("""
            SELECT * FROM movies
            WHERE title ILIKE %s
            AND (%s = '' OR genre = %s)
            ORDER BY rating DESC
        """, (search_value, genre, genre))

    elif sort == "rating_low":

        cursor.execute("""
            SELECT * FROM movies
            WHERE title ILIKE %s
            AND (%s = '' OR genre = %s)
            ORDER BY rating ASC
        """, (search_value, genre, genre))

    elif sort == "status":

        cursor.execute("""
            SELECT * FROM movies
            WHERE title ILIKE %s
            AND (%s = '' OR genre = %s)
            ORDER BY status ASC
        """, (search_value, genre, genre))

    else:

        cursor.execute("""
            SELECT * FROM movies
            WHERE title ILIKE %s
            AND (%s = '' OR genre = %s)
            ORDER BY title ASC
        """, (search_value, genre, genre))

    movies = cursor.fetchall()

    # Get all genres for the filter
    cursor.execute("""
        SELECT DISTINCT genre
        FROM movies
        WHERE genre IS NOT NULL
        AND genre != ''
        ORDER BY genre ASC
    """)

    genres = cursor.fetchall()

    return render_template(
        "lists.html",
        movies=movies,
        keyword=keyword,
        sort=sort,
        genre=genre,
        genres=genres
    )


# ---------------- INSERT PAGE ----------------

@app.route("/movie")
def movie():
    return render_template("insert.html")


# ---------------- ADD MOVIE ----------------

@app.route("/add_movie", methods=["POST"])
def add_movie():

    title = request.form["title"]
    genre = request.form["genre"]
    rating = request.form["rating"]
    status = request.form["status"]
    image_url = request.form.get("image_url", "")
    description = request.form.get("description", "")
    watch_url = request.form.get("watch_url", "")

    cursor.execute("""
        INSERT INTO movies(
            title,
            genre,
            rating,
            status,
            image_url,
            description,
            watch_url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        title,
        genre,
        rating,
        status,
        image_url,
        description,
        watch_url
    ))

    conn.commit()

    return redirect("/")


# ---------------- MOVIE DETAILS ----------------

@app.route("/movie/<int:id>")
def movie_details(id):

    cursor.execute(
        "SELECT * FROM movies WHERE id = %s",
        (id,)
    )

    movie = cursor.fetchone()

    return render_template(
        "movie_details.html",
        movie=movie
    )


# ---------------- DELETE MOVIE ----------------

@app.route("/delete/<int:id>")
def delete_movie(id):

    cursor.execute(
        "DELETE FROM movies WHERE id = %s",
        (id,)
    )

    conn.commit()

    return redirect("/")


# ---------------- EDIT PAGE ----------------

@app.route("/edit/<int:id>")
def edit_movie(id):

    cursor.execute(
        "SELECT * FROM movies WHERE id = %s",
        (id,)
    )

    movie = cursor.fetchone()

    return render_template(
        "edit.html",
        movie=movie
    )


# ---------------- UPDATE MOVIE ----------------

@app.route("/update/<int:id>", methods=["POST"])
def update_movie(id):

    title = request.form["title"]
    genre = request.form["genre"]
    rating = request.form["rating"]
    status = request.form["status"]
    image_url = request.form.get("image_url", "")
    description = request.form.get("description", "")
    watch_url = request.form.get("watch_url", "")

    cursor.execute("""
        UPDATE movies
        SET title = %s,
            genre = %s,
            rating = %s,
            status = %s,
            image_url = %s,
            description = %s,
            watch_url = %s
        WHERE id = %s
    """, (
        title,
        genre,
        rating,
        status,
        image_url,
        description,
        watch_url,
        id
    ))

    conn.commit()

    return redirect("/")


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)

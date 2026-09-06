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

# Add image_url column if an older table already exists
cursor.execute("""
ALTER TABLE movies
ADD COLUMN IF NOT EXISTS image_url TEXT
""")
cursor.execute("""
ALTER TABLE movies
ADD COLUMN IF NOT EXISTS description TEXT
""")

conn.commit()


# ---------------- HOME / MOVIE LIST ----------------

@app.route("/")
def home():

    keyword = request.args.get("keyword", "")
    sort = request.args.get("sort", "title")

    # Search + Sort
    if keyword:

        search_value = "%" + keyword + "%"

        if sort == "rating_high":
            cursor.execute("""
                SELECT * FROM movies
                WHERE title ILIKE %s
                ORDER BY rating DESC
            """, (search_value,))

        elif sort == "rating_low":
            cursor.execute("""
                SELECT * FROM movies
                WHERE title ILIKE %s
                ORDER BY rating ASC
            """, (search_value,))

        elif sort == "status":
            cursor.execute("""
                SELECT * FROM movies
                WHERE title ILIKE %s
                ORDER BY status ASC
            """, (search_value,))

        else:
            cursor.execute("""
                SELECT * FROM movies
                WHERE title ILIKE %s
                ORDER BY title ASC
            """, (search_value,))

    # Sort without search
    else:

        if sort == "rating_high":
            cursor.execute("""
                SELECT * FROM movies
                ORDER BY rating DESC
            """)

        elif sort == "rating_low":
            cursor.execute("""
                SELECT * FROM movies
                ORDER BY rating ASC
            """)

        elif sort == "status":
            cursor.execute("""
                SELECT * FROM movies
                ORDER BY status ASC
            """)

        else:
            cursor.execute("""
                SELECT * FROM movies
                ORDER BY title ASC
            """)

    movies = cursor.fetchall()

    return render_template(
        "lists.html",
        movies=movies,
        keyword=keyword,
        sort=sort
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
    description = request.form.get("description","")

    cursor.execute("""
        INSERT INTO movies(title, genre, rating, status, image_url, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (title, genre, rating, status, image_url, description))

    conn.commit()

    return redirect("/")

#---------------MOVIE DETAILS-------------
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
    description = request.form.get("description","")

    cursor.execute("""
        UPDATE movies
        SET title = %s,
            genre = %s,
            rating = %s,
            status = %s,
            image_url = %s,
            description = %s
        WHERE id = %s
    """, (title, genre, rating, status, image_url, description, id))

    conn.commit()

    return redirect("/")


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)

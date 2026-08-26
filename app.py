from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

# PostgreSQL connection
conn = psycopg2.connect(
    os.environ["DATABASE_URL"]
)

cursor = conn.cursor()

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

cursor.execute("""
ALTER TABLE movies
ADD COLUMN IF NOT EXISTS image_url TEXT
""")
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
image_url = request.form["image_url"]

cursor.execute("""
    INSERT INTO movies(title, genre, rating, status, image_url)
    VALUES (%s, %s, %s, %s, %s)
""", (title, genre, rating, status, image_url))

    conn.commit()

    return redirect("/")


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
image_url = request.form["image_url"]

cursor.execute("""
    UPDATE movies
    SET title = %s,
        genre = %s,
        rating = %s,
        status = %s,
        image_url = %s
    WHERE id = %s
""", (title, genre, rating, status, image_url, id))
    conn.commit()

    return redirect("/")


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)

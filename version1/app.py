@app.route('/urls', methods=['POST'])
def get_urls_post():
    form_data = request.form.to_dict()
    result = process_url_submission(form_data["url"])
    return handle_url_result(result)

#функция пытаеться добавить в БД URL
def process_url_submission(url: str) -> dict:
    try:
        validate_url(url)
        normalized_url = normalize_url(url)

        url_info = add_url(normalized_url)
        return {"id": url_info.id, "status": "created"}
    except psycopg2.errors.UniqueViolation:
        existing_url = find_by_name(normalized_url)
        if existing_url:
            return {"id": existing_url.id, "status": "duplicate"}
    except InvalidURLError:
        return {"status": "invalid"}
    except Exception:
        return {"status": "error"}

#функция работающая с результатом добавления url
def handle_url_result(result: dict) -> str:
    status = result.get("status")
    url_id = result.get("id")

    if status == "created":
        flash("Страница успешно добавлена", "alert-success")
        return redirect(url_for("get_one_url", id=url_id))
    elif status == "duplicate":
        flash("Страница уже существует", "alert-warning")
        return redirect(url_for("get_one_url", id=url_id))
    elif status == "invalid":
        flash("Некорректный URL", "alert-danger")
        return render_template("index.html"), 422
    else:
        flash("Произошла ошибка при добавлении URL", "alert-danger")
        return render_template("index.html"), 500
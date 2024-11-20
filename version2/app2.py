@app.route('/urls', methods=['POST'])
def get_urls_post():
    url = request.form['url']
    error_container = URLProcessingErrorContainer()
    return handle_url_submission(url, error_container)

#функция пытаеться добавить в БД URL
def process_url_submission(url, error_container):
    try:
        validate_url(url)
        normalized_url = normalize_url(url)

        existing_url = find_by_name(normalized_url)
        if existing_url:
            return {"status": "duplicate", "url_id": existing_url['id']}

        result = add_url(normalized_url)
        if result:
            return {"status": "success", "url_id": result['id']}

    except InvalidURLError as e:
        error_container.add_error(e.args[0], 422)
    except URLTooLongError as e:
        error_container.add_error(e.args[0], 422)
    except Exception as e:
        error_container.add_error("error", 500)


#функция работающая с результатом добавления URL
def handle_url_submission(url, error_container):
    result = process_url_submission(url, error_container)

    if error_container.has_errors():
        first_error = error_container.get_errors()[0]
        flash(first_error["message"], 'error')
        return render_template('index.html'), first_error["code"]

    elif result["status"] == "duplicate" or "success":
        return redirect(url_for('get_url_by_id', id=result["url_id"]))

    flash('Неизвестная ошибка', 'error')
    return render_template('index.html'), 500


#контейнер ошибок
class URLProcessingErrorContainer:
    def __init__(self):
        self.errors = []

    def add_error(self, message: str, code: int):
        self.errors.append({"message": message, "code": code})

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def get_errors(self) -> list:
        return self.errors
@app.route('/urls', methods=['POST'])
def add_url():
    return handle_url_submission()

________________________________________
#модель
def is_valid_url(url: str) -> bool:
    try:
        validate_url(url)
        return True
    except (InvalidURLError, URLTooLongError):
        return False

def is_url_duplicate(url: str) -> bool:
    with get_connection() as conn:
        return find_by_name(conn, url) is not None

def add_url_to_db(url: str) -> int:
    with get_connection() as conn:
        try:
            url_data = add_url(conn, url)
            return url_data.id
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return get_url_id(url)

def get_url_id(url: str) -> int:
    with get_connection() as conn:
        url_data = find_by_name(conn, url)
        return url_data.id if url_data else None
________________________________________
#контролер
def handle_url_submission():

    accepted_url = request.form.get('url')

    if not is_valid_url(accepted_url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html', invalid_value=accepted_url), 422

    normalized_url = normalize_url(accepted_url)

    if is_url_duplicate(normalized_url):
        flash('Страница уже существует', 'warning')
        url_id = get_url_id(normalized_url)
        return redirect(url_for('display_current_site', id=url_id))

    url_id = add_url_to_db(normalized_url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('display_current_site', id=url_id))
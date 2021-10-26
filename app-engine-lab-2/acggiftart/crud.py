# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from acggiftart import get_model, storage
from flask import Blueprint, current_app, redirect, render_template, request, \
    url_for


crud = Blueprint('crud', __name__)


# [START upload_image_file]
def upload_image_file(file):
    """
    Upload the user-uploaded file to Google Cloud Storage and retrieve its
    publicly-accessible URL.
    """
    if not file:
        return None

    public_url = storage.upload_file(
        file.read(),
        file.filename,
        file.content_type
    )

    current_app.logger.info(
        "Uploaded file %s as %s.", file.filename, public_url)

    return public_url
# [END upload_image_file]


@crud.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    artworks, next_page_token = get_model().list(cursor=token)

    return render_template(
        "list.html",
        artworks=artworks,
        next_page_token=next_page_token)


@crud.route('/<id>')
def view(id):
    artwork = get_model().read(id)
    return render_template("view.html", artwork=artwork)


@crud.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        # If an image was uploaded, update the data to point to the new image.
        # [START image_url]
        image_url = upload_image_file(request.files.get('photo'))
        # [END image_url]

        # [START image_url2]
        if image_url:
            data['photoUrl'] = image_url
        # [END image_url2]

        artwork = get_model().create(data)

        return redirect(url_for('.view', id=artwork['id']))

    return render_template("form.html", action="Add", artwork={})


@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    artwork = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        image_url = upload_image_file(request.files.get('photo'))

        if image_url:
            data['photoUrl'] = image_url

        artwork = get_model().update(data, id)

        return redirect(url_for('.view', id=artwork['id']))

    return render_template("form.html", action="Edit", artwork=artwork)


@crud.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))

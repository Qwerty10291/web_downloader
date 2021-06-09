var state = null;
$('#add_document').click(create_add_row)
$('#update').click(update)
$('#start').click(start_loading)

function update(){
    update_state()
    load_documents()
}
function update_state(){
    $.get('/status', function (data){
        if(data.status)
            $('#status').text('в процессе')
        else
            $('#status').text('загрузка не идет')
    })
}

function load_documents() {
    $.get('/api/docs', create_document_rows)
}

function start_loading() {
    $.get('/start', function(data){
        if(handle_error(data))
            alert('загрузка началась')
            load_documents()
    })
}

function create_document_rows(data) {
    console.log(data)
    state = data;
    docs_container = $('#content').empty()
    for (let document of data) {
        let container = create_document_row(document)
        docs_container.append(container)
    }
}

function create_document_row(document) {
    let container = $('<div class="d-flex flex-row aling-items-center content-row"></div>');
    let id = $(`<span class='doc_id text-primary'>${document.id}</span>`);
    let login = $(`<span class="doc_login">${document.user.login}</span>`);
    let password = $(`<span class="doc_password">${document.user.password}</span>`);
    let doc_name = $(`<span class="doc_name">${document.name}</span>`);
    let link = $(`<a href="${document.link}" class="doc_link text-truncate">${document.link}</a>`);
    let flag = $(`<span class="doc_flag">${document.flag}</span>`)

    let state = null
    if (document.state) {
        if (document.state == 'auth error')
            state = $(`<span class="doc_status ms-auto text-danger">ошибка авторизации</span>`)
        else if (document.state == 'download error')
            state = $(`<span class="doc_status ms-auto text-danger">ошибка загрузки</span>`)
        else
            state = $(`<span class="doc_status ms-auto">${document.state}</span>`)
    } else
        state = $(`<span class="doc_status ms-auto">не загружен</span>`)

    let button_container = $(`<div class="doc-buttons d-inline-flex flex-row"></div>`)
    let button_delete = $(`<button class="btn btn-danger">Удалить</button>`).click(function () { delete_document(container, document.id) })
    let button_change = $(`<button class="btn btn-primary">Изменить</button>`).click(function () {create_update_row(container, document)})
    let button_load = $(`<a href="/download/docs/${document.id}" class="btn btn-success">Скачать</a>`)
    button_container.append(button_delete).append(button_change).append(button_load)
    container.append(id).append(login).append(password).append(doc_name).append(flag).append(link).append(state).append(button_container)
    return container
}

function delete_document(container, id) {
    if (confirm(`Вы действительно хотите удалить документ?`)) {
        $.ajax({
            url: `/api/docs/${id}`,
            type: 'DELETE',
            contentType: 'application/json',
            success: function (data) {
                if (handle_error(data)) {
                    console.log(this.container)
                    this.container.remove();
                }
            }.bind({ 'container': container })
        })
    }
}

function create_add_row() {
    let container = $(`<div class="d-flex flex-row aling-items-center content-row"></div>`)
    let login = $(`<input type="text" class="doc_login" placeholder='логин'>`)
    let password = $(`<input type="text" class="doc_password" placeholder='пароль'>`)
    let name = $(`<input class='doc_name' type="text" value="" placeholder='название'>`)
    let link = $(`<input type="text" class="doc_link" placeholder='ссылка'>`)
    let flag = $(`<select class="doc_state">
                    <option value="false">false</option>
                    <option value="true">true</option>
                    <option value="archive">archive</option>
                </select>`)
    let button_container = $(`<div class="doc-buttons d-inline-flex flex-row ms-auto"></div>`)
    let button_create = $(`<button class="btn btn-success">Добавить</button>`).click(function () {
        let data = {
            login: login.val(),
            password: password.val(),
            name: name.val(),
            link: link.val(),
            flag: flag.val()
        }
        post_new_document(container, data)
    })
    let button_cancel = $(`<button class="btn btn-danger">Отмена</button>`).click(function () {
        container.remove()
    })

    button_container.append(button_cancel).append(button_create)
    container.append(login).append(password).append(name).append(link).append(flag).append(button_container)
    $('#content').append(container)
}

function create_update_row(container, document){
    let container_new = $(`<div class="d-flex flex-row aling-items-center content-row"></div>`)
    let login = $(`<input type="text" class="doc_login" placeholder='логин'>`).val(document.user.login)
    let password = $(`<input type="text" class="doc_password" placeholder='пароль'>`).val(document.user.password)
    let name = $(`<input class='doc_name' type="text" value="" placeholder='название'>`).val(document.name)
    let link = $(`<input type="text" class="doc_link" placeholder='ссылка'>`).val(document.link)
    let flag = $(`<select class="doc_state">
                    <option value="false">false</option>
                    <option value="true">true</option>
                    <option value="archive">archive</option>
                </select>`)
    let button_container = $(`<div class="doc-buttons d-inline-flex flex-row ms-auto"></div>`)
    let button_create = $(`<button class="btn btn-success">Изменить</button>`).click(function () {
        let data = {
            login: login.val(),
            password: password.val(),
            name: name.val(),
            link: link.val(),
            flag: flag.val(),
            id: document.id,
        }
        update_document(container_new, data)
    })
    let button_cancel = $(`<button class="btn btn-danger">Отмена</button>`).click(function (){
        container_new.replaceWith(container)
    })
    button_container.append(button_cancel).append(button_create)
    container_new.append(login).append(password).append(name).append(link).append(flag).append(button_container)
    container.replaceWith(container_new)
}


function handle_error(object) {
    console.log(object)
    if (object.error) {
        alert('ошибка' + object.error)
        return false
    }
    return true
}

function post_new_document(container, data) {
    $.post('/api/docs', data).done(
        function (response) {
            if (handle_error(response)) {
                data.id = response.id
                data.user = {
                    login: data.login,
                    password: data.password
                }
                container.replaceWith(create_document_row(data))
    }})}


function update_document(container, datas){
    let id = datas.id
    delete datas.id
    console.log(datas)
    $.ajax({
        url: '/api/docs/' + id,
        type: 'PUT',
        data: JSON.stringify(datas),
        contentType: 'application/json',
        success: function (response){
            console.log(response)
            if(handle_error(response)){
                update_passwords(response.document.user.login, response.document.user.password)
                console.log(container)
                container.replaceWith(create_document_row(response.document));
            }
        }
    })
}

function update_passwords(l, p){
    for(let container of $('.content-row')){
        let login = container.querySelector('.doc_login')
        let password = container.querySelector('.doc_password')
        if (login.innerHTML == l)
            password.innerHTML = p;
    }
}
update()
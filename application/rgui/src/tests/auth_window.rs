use gdk;
use gtk::{IsA, Object, Widget as GtkWidget};
use relm::{self, Component, Widget, Update};
use relm_test::*;
use widgets::text_input::{TextInputMsg, TextInput};
use diesel::prelude::*;


fn set_text_input<W: Clone + IsA<Object> + IsA<GtkWidget>>(widget: &W, string: &str) {
    let input = find_widget_by_name(widget, "input").unwrap();
    focus(&input);
    enter_keys(&input, string);
}

#[test]
fn test_auth() {
    use ::windows::auth_window::WinMsg::*;

    {
        let conn = &*::rapi::DB_POOL.get().unwrap();
        conn.begin_test_transaction().unwrap();
        ::rapi::users::User::add(&conn, "coucou", "coucou").unwrap();
    }


    let (component, widgets) = relm::init_test::<::windows::auth_window::Win>(()).unwrap();

    set_text_input(widgets.login_input.widget(), "coucou");
    set_text_input(widgets.password_input.widget(), "coucou");

    let model_observer = observer_new!(component, RecvModel(_));
    component.stream().emit(GetModel);
    observer_wait!(let RecvModel(model) = model_observer);
    assert!(!model.ok);

    click(&widgets.validate_button);

    component.stream().emit(GetModel);
    observer_wait!(let RecvModel(model) = model_observer);
    assert!(model.ok);
}

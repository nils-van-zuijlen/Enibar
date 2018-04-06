use gdk;
use relm::{self, Component, Widget, Update};
use relm_test::{click, Observer, enter_key, enter_keys};
use widgets::text_input::{TextInputMsg, TextInput};
use schema::connection;


#[test]
fn test_auth() {
    use ::windows::auth_window::WinMsg::*;

    let (component, widgets) = relm::init_test::<::windows::auth_window::Win>(()).unwrap();
    enter_keys(widgets.login_input.widget(), "coucou");
    // FIXME: We can't focus a Box for now so this has to be here
    enter_key(widgets.login_input.widget(), gdk::enums::key::Tab);
    enter_keys(widgets.password_input.widget(), "coucou");

    let model_observer = observer_new!(component, RecvModel(_));
    component.stream().emit(GetModel);
    observer_wait!(let RecvModel(model) = model_observer);
    assert!(!model.ok);

    click(&widgets.validate_button);

    component.stream().emit(GetModel);
    observer_wait!(let RecvModel(model) = model_observer);
    assert!(model.ok);
}

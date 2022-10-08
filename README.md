# Dat250-2022 Group 2

List of vurnebilities from social insecurity:

- [X] Broken Authentication - No safe way to prove who you are and no password rules.   **Solved by using flask login**
     - [x] Insufficient Logging & Monitoring -No' time out  **Session timeout with flask.session.**
     - [ ] Attemt restrictstions. Idea to solving, using limiter however importing get_remote_adress wouldnt work to out favour
     - [X] Hashing password.  **Solved by using Hashlib_SHA256**
     - [x] passwrod requirements  **adding requirements**
     
- [X] Broken access control - change of the url. People has full access to others account by path traversing.   **Solved by using flask login**
- [x] Unrestricted File Upload - can upload anythiong.        **Checking extentions of files**
- [ ] Website error when inputting ' " '
- [x] clickjacking   **Solved by adding X-Frame-Options = SAMEORIGIN on header**
- [x] no Anti-CSRF   **Solved by adding form.csrf_token() on each form html**
- [x] X-content type option header missing  - risk to xss attack   **Solved by adding X-Content-Type-Options = nosniff on header**
- [x] cookie thieving **Solved by adding Samesite=strict on app.config**
- [ ] cross domain config
- [x] content secure policy   **Solved by adding security to base.html header**
- [x] Unupdated Libaries.  **Solved by updating to a the latest version**
- [x] updating libaries. example flask 1.1.1 to flask 2.2.2
- [x] resolving Errors in console log
- [ ] when typing "username" in adding friends, the first registered account will be added. Doing it again will result in an error page
- [x] adding session protection

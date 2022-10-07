# Dat250-2022 Group 2

List of vurnebilities from social insecurity:

- [ ] w	Broken Authentication - No safe way to prove who you are and no password rules.  **Solved by using flask login**
- [ ] w	Broken access control - change of the url. People has full access to others account by path traversing. **Solved by using flask login**
- [ ] Insufficient Logging & Monitoring -No' time out / attemt restrictions, makes it eligible for brute force attacks. 
- [x]	Unrestricted File Upload - can upload anythiong. **Checking extentions of files**
- [ ] w	Hashing password. solved by using flask login
- [ ]	Website error when inputting "
- [x]	clickjacking **Solved by adding X-Frame-Options = SAMEORIGIN on header**
- [x]	no Anti-CSRF **Solved by adding form.csrf_token() on each form html**
- [x]	X-content type option header missing  - risk to xss attack **Solved by adding X-Content-Type-Options = nosniff on header**
- [ ]	cookie can be scooped
- [ ]	cross domain config
- [ ]	content secure policy
- [x] Unupdated Libaries. **Solved by updating to a the latest version**

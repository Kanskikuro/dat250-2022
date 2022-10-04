# Dat250-2022 Group 2

List of vurnebilities from social insecurity:

- [ ] w	Broken Authentication - No safe way to prove who you are and no password rules.  **Solved by using flask login**
- [ ] w	Broken access control - change of the url. People has full access to others account by path traversing. **Solved by using flask login**
- [ ] w	Insufficient Logging & Monitoring -No' time out / attemt restrictions, makes it eligible for brute force attacks. 
- [x]	Unrestricted File Upload - can upload anythiong. **Checking extentions of files**
- [ ] w	Hashing password. solved by using flask login
- [ ]	Website error when inputting "
- [ ]	clickjacking
- [x]	no Anti-CSRF **Solved by**
- [ ]	X-content type option header missing  - risk to xss attack
- [ ]	cookie can be scooped
- [ ]	cross domain config
- [ ]	content secure policy

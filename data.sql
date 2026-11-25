INSERT INTO Authors(author_id, name) VALUES
(1, 'Veronica Haddon'),
(2, 'Everett Ferguson'),
(3, 'Mary Fabyan Windeatt'),
(4,  'Allen Gersho'),
(5, 'Fiona Cownie'),
(6, 'Kenneth H. Cooper'),
(7, 'Sonia Rivera-Valdes'),
(8,  'Stefan Draminski'),
(9, 'Kayode J. Fakinlede'),
(10, 'Sydney Walker'),
(11, 'Sue Walters'),
(12, 'Evan Gerstmann'),
(13, 'Jerry Baker'),
(14, 'Mark Graham'),
(15, 'Graham Robson');


INSERT INTO Books (book_id, title, publisher, price, summary, stock, is_active, author_id) VALUES
(1, 'Whispers of the Wicked Saints', 'iUniverse', 10.95, 'Julia Thomas finds her life spinning out of control after the death of her husband, Richard.', 20, True, 1),
(2, 'The Church of Christ: A Biblical Ecclesiology for Today', 'Wm. B. Eerdmans Publishing', 25.97,'Respected biblical scholar Everett Ferguson presents a genuine biblical theology of the church.', 12, TRUE, 2),
(3, 'Saint Hyacinth of Poland', 'Tan Books & Pub', 13.95, 'The story for children 10 and up of St. Hyacinth, the Dominican who planted the Faith in Poland, Lithuania and Russia and worked many miracles.', 30, TRUE, 3),
(4, 'Vector Quantization and Signal Compression (The Springer International Series in Engineering and Computer Science)', 'Springer Science & Business Media', 76.94, 'This book is devoted to the theory and practice of signal compression, applied to signals such as speech, audio, images, and video.', 8, TRUE, 4),
(5, 'The Ultimate Guide to Law School Admission: Insider Secrets for Getting a "Big Envelope" with Your Acceptance to Law School!', 'Bloomsbury Publishing', 14.95, 'This collection brings together a distinguished group of researchers to examine the power relations played out in university law schools.', 25, TRUE, 5),
(6, 'Overcoming Hypertension (Dr. Kenneth H. Cooper''s Preventive Medicine Program)','Bantam', 23.00, 'Like a time bomb ticking away, hypertension builds quietly, gradually, placing unbearable strain on the body.', 18, TRUE, 6),
(7, 'The Forbidden Stories of Marta Veneranda', 'Seven Stories Press', 21.95, 'Marta Veneranda, a Latina neoyorkina, finds that she inspires the confessional in people.', 15, TRUE, 7),
(8, 'The Battleship Bismarck', 'Bloomsbury Publishing', 34.95, 'The Bismarck is perhaps the most famous and notorious warship ever built.', 10, TRUE, 8),
(9, 'Beginner''s Yoruba (Hippocrene Beginner''s Series)', 'Hippocrene Books', 19.77, 'An introduction to the Yoruba language, spoken by over 30 million people in south-western Nigeria, parts of the Benin Republic, and Togo.', 22, TRUE, 9),
(10, 'A Dose of Sanity: Mind, Medicine, and Misdiagnosis', 'Wiley', 30.00, 'Each year, hundreds of thousands of Americans suffering from common medical conditions are misdiagnosed with psychiatric disorders.', 14, TRUE, 10),
(11, 'Pyrography Designs', 'Fox Chapel Publishing Company Incorporated', 13.19, 'This book offers 30 North American wildlife illustrations and 10 border designs to use in woodburning projects.', 35, TRUE, 11),
(12, 'Academic Freedom after September 11', 'Stanford University Press', 22.95, 'This is a provocative examination of the current state of academic freedom in the United States and around the world.', 9, TRUE, 12),
(13, 'The Impatient Gardener''s Lawn Book', 'Random House Digital, Inc.', 12.95, 'Explains how to grow a green, beautiful lawn and offers advice on fertilizers, watering, and lawn diseases.', 40, TRUE, 13),
(14, 'Josef Fuchs on Natural Law (Moral Traditions series)', 'Georgetown University Press', 48.82, 'This is the first full-length analysis of Fuchs''s efforts to reconstruct Roman Catholic natural law theory.', 6, TRUE, 14),
(15, 'Audi Quattro: The Complete Story', 'Veloce Publishing Ltd', 37.95, 'The Audi Quattro was the world''s first successful four-wheel-drive rally car.', 11, TRUE, 15);


INSERT INTO Members (member_id, name, email, password_hash, role) VALUES
(1, 'Nishan Bhattarai', 'nishan.bhattarai@sjsu.edu', 'scrypt:32768:8:1$LumtRDNYE08b8p7j$eaa86a9f0e52fd33a40aa30ee6d3afc536eb1bb75328cfb8830a4a0f48557f169376b7eb0a9a7209d624991fc8cee5fe9ed8ac890d1cbd9d573f2a3105584371', 'admin'),
(2, 'Kelvin Phat', 'kelvin.phat@sjsu.edu', 'scrypt:32768:8:1$LumtRDNYE08b8p7j$eaa86a9f0e52fd33a40aa30ee6d3afc536eb1bb75328cfb8830a4a0f48557f169376b7eb0a9a7209d624991fc8cee5fe9ed8ac890d1cbd9d573f2a3105584371', 'admin'),
(3, 'Andy Martin Valencia', 'andy.martinvalencia@sjsu.edu', 'scrypt:32768:8:1$LumtRDNYE08b8p7j$eaa86a9f0e52fd33a40aa30ee6d3afc536eb1bb75328cfb8830a4a0f48557f169376b7eb0a9a7209d624991fc8cee5fe9ed8ac890d1cbd9d573f2a3105584371', 'admin'),
(4, 'James Carter', 'james.carter@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(5, 'Maria Lopez',  'maria.lopez@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(6, 'Anthony Gordan', 'anthony.gordan@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(7, 'Pablo Gavi',   'pablo.gavi@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(8, 'Priya Sharma', 'priya.sharma@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(9, 'Dani Olmo', 'dani.olmo@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(10, 'Karim Adeyemi', 'karim.adeyemi@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(11, 'Joan Garcia', 'joan.garcia@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(12, 'Marc Bernal', 'marc.bernal@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(13, 'Lamin Yamal', 'lamin.yamal@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(14, 'Gerard Martin', 'gerard.martin@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer'),
(15, 'Pau Cubarsi', 'pau.cubarsi@example.com', 'scrypt:32768:8:1$OSjmPBDpAECVRjg9$c12fc321fd87ec41800d7e7b302fb67d2ea4bff69c50c0a6f4947aee66622ccf88481a9c9318216ad2166d9c0077094381283563771844d2e1710bfba2caf1e9', 'customer');
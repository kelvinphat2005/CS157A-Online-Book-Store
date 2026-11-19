-- CS 157A - Online Book Store
-- Authors -> Books; Members -> Orders; Orders + Books -> OrderLine;
-- Members + Books -> Reviews.

-- drop existing tables so this script can be rerun.
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS OrderLine;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Members;
DROP TABLE IF EXISTS Authors;


-- ============================================================
-- 1. Authors - Nishan
-- ============================================================
CREATE TABLE Authors(
    author_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,

    PRIMARY KEY(author_id)
);



-- ============================================================
-- 2. Members - Kelvin
-- ============================================================

CREATE TABLE Members (
    member_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'customer',

    PRIMARY KEY (member_id),

    CONSTRAINT uq_members_email UNIQUE (email),

    CONSTRAINT chk_members_role CHECK (role IN ('customer', 'admin'))
);



-- ============================================================
-- 3. Books - Kelvin
-- ============================================================

CREATE TABLE Books (
    book_id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    author_id INT NOT NULL,
    publisher VARCHAR(100),
    summary TEXT,
    stock INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    price DECIMAL(10, 2) NOT NULL,

    PRIMARY KEY (book_id),

    CONSTRAINT fk_books_author FOREIGN KEY (author_id) REFERENCES Authors(author_id) ON DELETE RESTRICT,

    CONSTRAINT chk_books_stock CHECK (stock >= 0),

    CONSTRAINT chk_books_price CHECK (price >= 0)
);



-- ============================================================
-- 4. Orders - ANDY
-- ============================================================

CREATE TABLE Orders (
    order_id INT NOT NULL AUTO_INCREMENT,
    member_id INT NOT NULL,
    fulfillment_type VARCHAR(10) NOT NULL,
    fulfillment_address VARCHAR(255) NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',

    PRIMARY KEY (order_id),

    CONSTRAINT fk_orders_member
        FOREIGN KEY (member_id) REFERENCES Members(member_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_orders_fulfillment_type
        CHECK (fulfillment_type IN ('pickup', 'delivery')),

    CONSTRAINT chk_orders_total_cost
        CHECK (total_cost >= 0)
) ENGINE = InnoDB;


-- ============================================================
-- 5. OrderLine - ANDY
-- ============================================================

CREATE TABLE OrderLine (
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,

    PRIMARY KEY (order_id, book_id),

    CONSTRAINT fk_orderline_order
        FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_orderline_book
        FOREIGN KEY (book_id) REFERENCES Books(book_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_orderline_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_orderline_price
        CHECK (price >= 0)
) ENGINE = InnoDB;


-- ============================================================
-- 6. Reviews - Nishan
-- ============================================================

CREATE TABLE Reviews (
    review_id INT NOT NULL AUTO_INCREMENT,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    rating TINYINT NOT NULL,
    review_text TEXT NOT NULL,

    PRIMARY KEY (review_id),

    CONSTRAINT fk_reviews_book
        FOREIGN KEY (book_id) REFERENCES Books(book_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_reviews_member
        FOREIGN KEY (member_id) References Members(member_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_reviews_member_book
        UNIQUE (member_id, book_id),

    CONSTRAINT chk_reviews_rating
        CHECK (rating BETWEEN 1 AND 5)
);




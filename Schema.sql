-- CS 157A - Online Book Store
-- Authors -> Books; Members -> Orders; Orders + Books -> OrderLine;
-- Members + Books -> Reviews.


-- ============================================================
-- 1. Authors - Nishan
-- ============================================================
-- Paste the complete CREATE TABLE Authors statement here.
-- Expected columns: author_id (primary key), name.



-- ============================================================
-- 2. Members - Kelvin
-- ============================================================
-- Paste the complete CREATE TABLE Members statement here.
-- Expected columns: member_id (primary key), name, email (UNIQUE),
--                   password_hash, role.
-- member_id must be a signed INT to match Orders.member_id.



-- ============================================================
-- 3. Books - Kelvin
-- ============================================================
-- Paste the complete CREATE TABLE Books statement here.
-- Expected columns: book_id (primary key), title, author_id (foreign key),
--                   publisher, summary, stock, is_active, price.
-- book_id must be a signed INT to match OrderLine.book_id.
-- Authors must be created before Books.



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
-- Paste the complete CREATE TABLE Reviews statement here.
-- Expected columns: review_id (primary key), book_id (foreign key),
--                   member_id (foreign key), rating, review_text.
-- Books and Members must be created before Reviews.


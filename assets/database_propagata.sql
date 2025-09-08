CREATE TABLE "business" (
                            "businessID" VARCHAR PRIMARY KEY,
                            "name" VARCHAR UNIQUE,
                            "street" VARCHAR,
                            "postCode" VARCHAR,
                            "town" VARCHAR,
                            "country" VARCHAR,
                            "vatNo" VARCHAR UNIQUE,
                            "bic" VARCHAR UNIQUE,
                            "iban" VARCHAR,
                            "phone" VARCHAR,
                            "email" VARCHAR,
                            "logo" BYTEA
);
CREATE TABLE "client" (
                          "clientID" VARCHAR PRIMARY KEY,
                          "name" VARCHAR UNIQUE,
                          "street" VARCHAR,
                          "postCode" VARCHAR,
                          "town" VARCHAR,
                          "country" VARCHAR,
                          "vatNo" VARCHAR UNIQUE
);

CREATE TABLE "invoice" (
                           "invoiceID" VARCHAR PRIMARY KEY,
                           "invoiceNo" VARCHAR,
                           "currency" VARCHAR,
                           "vatPercent" INTEGER,
                           "issuedAt" VARCHAR,
                           "dueTo" VARCHAR,
                           "note" VARCHAR,
                           "business_id" VARCHAR REFERENCES "business"("businessID"),
                           "client_id" VARCHAR REFERENCES "client"("clientID"),
                           "language" VARCHAR
);

CREATE TABLE "product" (
                           "productID" VARCHAR PRIMARY KEY,
                           "description" VARCHAR,
                           "quantity" FLOAT,
                           "unit" VARCHAR,
                           "price" FLOAT,
                           "invoice_id" VARCHAR REFERENCES "invoice"("invoiceID")
);

CREATE TABLE "user" (
    "userID" VARCHAR PRIMARY KEY,
    "username" VARCHAR UNIQUE,
    "password" VARCHAR,
    "business_ids" VARCHAR[]
);

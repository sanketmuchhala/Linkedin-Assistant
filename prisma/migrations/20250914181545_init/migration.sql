-- CreateTable
CREATE TABLE "ConnectionRecord" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "fullName" TEXT NOT NULL,
    "role" TEXT,
    "company" TEXT,
    "linkedinUrl" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "whyConnect" TEXT NOT NULL,
    "sharedTopics" TEXT NOT NULL DEFAULT '[]',
    "evidence" TEXT NOT NULL DEFAULT '[]',
    "tone" TEXT,
    "doNotDo" TEXT NOT NULL DEFAULT '[]',
    "goal" TEXT,
    "cta" TEXT,
    "tags" TEXT NOT NULL DEFAULT '[]',
    "status" TEXT NOT NULL DEFAULT 'DRAFT',
    "connectionNote" TEXT,
    "acceptanceDM" TEXT,
    "nextActionDate" DATETIME,
    "nextActionLabel" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL
);

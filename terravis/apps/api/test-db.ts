import { PrismaClient } from "./generated/prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";

// Prisma 7 requires an explicit "driver adapter" -- this is the actual
// low-level Postgres driver Prisma Client sits on top of. We point it
// at the same DATABASE_URL from .env.
const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL });
const prisma = new PrismaClient({ adapter });

async function main() {
  // Create a test user
  const user = await prisma.user.create({
    data: { email: "test@terravis.dev" },
  });
  console.log("Created user:", user);

  // Create a test job linked to that user
  const job = await prisma.job.create({
    data: {
      task: "CLOUD_REMOVAL",
      inputFileUrl: "https://example.com/fake-input.tif",
      userId: user.id,
    },
  });
  console.log("Created job:", job);

  // Read it back, including the related user (this is what `include` does --
  // it's like a SQL JOIN, fetching related rows in one query)
  const jobWithUser = await prisma.job.findUnique({
    where: { id: job.id },
    include: { user: true },
  });
  console.log("Job with user attached:", jobWithUser);
}

main()
  .catch((e) => console.error(e))
  .finally(() => prisma.$disconnect()); // always close the connection when done

import { Client } from "@hubspot/api-client";
import * as dotenv from "dotenv";
dotenv.config();

const client = new Client({ accessToken: process.env.HUBSPOT_ACCESS_TOKEN });

export async function upsertContact(candidate) {
  const properties = {
    email: candidate.email,
    firstname: candidate.first_name,
    lastname: candidate.last_name,
    phone: candidate.phone,
    jobtitle: candidate.current_title,
  };

  // Step 1 — search for existing contact by email
  const searchResult = await client.crm.contacts.searchApi.doSearch({
    filterGroups: [
      {
        filters: [
          {
            propertyName: "email",
            operator: "EQ",
            value: candidate.email,
          },
        ],
      },
    ],
    properties: ["id", "email"],
    limit: 1,
  });

  // Step 2 — update if exists, create if not
  if (searchResult.results.length > 0) {
    const contactId = searchResult.results[0].id;
    await client.crm.contacts.basicApi.update(contactId, { properties });
    console.log(`Updated existing contact: ${contactId} (${candidate.email})`);
    return { action: "updated", hubspot_id: contactId };
  } else {
    const created = await client.crm.contacts.basicApi.create({ properties });
    console.log(`Created new contact: ${created.id} (${candidate.email})`);
    return { action: "created", hubspot_id: created.id };
  }
}

import { WebClient } from "@slack/web-api";

const slack = new WebClient(
  process.env.SLACK_BOT_TOKEN
);


console.log(
  "Slack token loaded:",
  !!process.env.SLACK_BOT_TOKEN
);

export async function sendNewCandidateAlert(
  email,
  source
) {

  try {

        const authTest =
            await slack.auth.test();

        console.log(
            "Slack identity:",
            authTest
        );

    const result =
      await slack.chat.postMessage({

        channel: "#new-candidates",

        text:
`🆕 New Candidate

Email: ${email}
Source: ${source}`
      });

    console.log(
      "Slack API response:",
      result.ok
    );

  }
  catch(error){

    console.error(
      "Slack error:",
      error.data || error.message
    );

    throw error;
  }
}
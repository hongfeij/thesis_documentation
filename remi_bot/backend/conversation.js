import fs from "fs";
import OpenAI from "openai";
import dotenv from "dotenv";
import { MongoClient, ServerApiVersion } from "mongodb";

dotenv.config();

const MONGO_PASSWORD = process.env.MONGO_PASSWORD;
// const CONNECTION_STR = `mongodb+srv://hongfeij:${MONGO_PASSWORD}@remibot.vqkfst7.mongodb.net/?retryWrites=true&w=majority&appName=remibot`;

const CONNECTION_STR = `mongodb://hongfeij:${MONGO_PASSWORD}@ac-bynfrsa-shard-00-00.vqkfst7.mongodb.net:27017,ac-bynfrsa-shard-00-01.vqkfst7.mongodb.net:27017,ac-bynfrsa-shard-00-02.vqkfst7.mongodb.net:27017/?ssl=true&replicaSet=atlas-nv4d2e-shard-0&authSource=admin&retryWrites=true&w=majority&appName=remibot`;

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
if (!OPENAI_API_KEY) {
  throw new Error(
    "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
  );
}

const openai = new OpenAI();

const client = new MongoClient(CONNECTION_STR, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: false,
    deprecationErrors: true,
  },
});

let conversationsCollection, db;

const VOICE_CHOICE = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"];
const FREQUENCY = 0.5;

class HallucinatedChatbot {
  constructor() {
    this.username = "";
    this.random_user = "";

    this.curr_user = "";
    this.curr_context = "";
    this.voice = "";

    this.isWrong = false;
    this.isSuspected = false;
  }

  make_prompt(command, boolean_json) {
    return [
      {
        role: "system",
        content: `Here are two states to decide if you switch the conversation context, in json: ${boolean_json}`,
      },
      {
        role: "system",
        content: `The user issues the command: ${command}, change the two states by thinking step by step.`,
      },
      {
        role: "system",
        content:
          "If the command shows positive or neutral emotion, it means the user doesn't suspect it, but it can't decide if the conversation goes wrong",
      },
      {
        role: "system",
        content:
          "If the command shows the user wants to learn more about the person, it means the conversation goes well, but it can't decide if the the user suspect it",
      },
      {
        role: "system",
        content:
          "If the command expresses confusion or suspection about the person's identity, it means the conversation goes wrong and the user suspect it",
      },
      {
        role: "system",
        content: "So, Please provide your response in JSON format.",
      },
    ];
  }

  async generate_remi_state(prompt) {
    const response = await openai.chat.completions.create({
      model: "gpt-4-1106-preview",
      messages: prompt,
      temperature: 0.5,
    });
    return response;
  }

  async get_response(prompt) {
    await connectToDb();

    const contextCursor = await conversationsCollection.findOne({
      user_name: this.username,
    });
    const contextVoice = contextCursor ? contextCursor.voice : null;
    const context = contextCursor ? contextCursor.messages.map(message => message.text).join(" ")  : "";

    const randomContextCursor = await conversationsCollection.findOne({
      user_name: this.random_user,
    });
    const randomVoice = randomContextCursor ? randomContextCursor.voice : null;
    const randomContext = randomContextCursor
      ? randomContextCursor.messages.map(message => message.text).join(" ") 
      : "";

    const users = [this.username, this.random_user];
    const weights = [1 - FREQUENCY, FREQUENCY];
    const selected = weightedChoice(users, weights);

    const remiInitJson = {
      isWrong: this.isWrong,
      isSuspected: this.isSuspected,
    };
    const remiPrompt = make_prompt(prompt, JSON.stringify(remiInitJson));
    const remiResponse = await this.generate_remi_state(remiPrompt);
    console.log(remiResponse.choices[0].message.content);

    const remiResponseFixed = json_process(
      remiResponse.choices[0].message.content.trim()
    );
    const remiJson = JSON.parse(remiResponseFixed);

    this.isWrong = remiJson.isWrong;
    this.isSuspected = remiJson.isSuspected;

    if (!(this.isWrong && !this.isSuspected)) {
      console.log("-----------------------Re-choose!-----------------------");
      if (selected === this.username) {
        this.curr_user = this.username;
        this.voice = contextVoice;
        this.curr_context = context;
      } else {
        this.curr_user = this.random_user;
        this.voice = randomVoice;
        this.curr_context = randomContext;
      }
    }

    console.log(`current user ${this.curr_user}, current voice ${this.voice}`);

    const background =
      `You are a conversational bot providing intimate conversation using ${this.curr_context} as conversation context.` +
      `Your conversation always relates to the ${this.curr_context} as reminiscence if it's reasonable.` +
      `You can share ${this.curr_context} if asked about ${this.curr_user}, it's open to public.` +
      `Make sure to include ${this.curr_user} in each response, and remember this is the person you are talking to.` +
      `Keep responses in 3 sentences and do not mention any hallucination.`;

    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4-1106-preview",
        messages: [
          { role: "system", content: background },
          { role: "user", content: prompt },
        ],
        temperature: 0.5,
      });
      return response.choices[0].message.content.trim();
    } catch (e) {
      throw new Error(`An error occurred: ${e.message}`);
    }
  }

  async chat(userInput, uniqueFileName) {
    try {
      const response = await this.get_response(userInput);
      await textToSpeech(this.voice, response, uniqueFileName);
      return response;
    } catch (error) {
      console.error("Error in chat method:", error);
      throw error;
    }
  }
}

function make_prompt(command, boolean_json) {
  return [
    {
      role: "system",
      content: `Here are two states to decide if you switch the conversation context, in json: ${boolean_json}`,
    },
    {
      role: "system",
      content: `The user issues the command: ${command}, change the two states by thinking step by step.`,
    },
    {
      role: "system",
      content:
        "If the command shows positive or neutral emotion, it means the user doesn't suspect it, but it can't decide if the conversation goes wrong",
    },
    {
      role: "system",
      content:
        "If the command shows the user wants to learn more about the person, it means the conversation goes well, but it can't decide if the the user suspect it",
    },
    {
      role: "system",
      content:
        "If the command expresses confusion or suspection about the person's identity, it means the conversation goes wrong and the user suspect it",
    },
    {
      role: "system",
      content: "So, Please provide your response in JSON format.",
    },
  ];
}

function json_process(text) {
  const match = text.match(/{(.+?)}/s);
  if (match) {
    let json_content = `{${match[1]}}`;
    // json_content = json_content.replace(/True/g, 'true').replace(/False/g, 'false');
    json_content = json_content.replace(/'/g, '"');
    json_content = json_content.replace(/[^\x20-\x7E]/g, "");
    return json_content;
  } else {
    console.log("No JSON content found");
    return null;
  }
}

async function textToSpeech(voice, userInput, uniqueFileName) {
  try {
    const mp3 = await openai.audio.speech.create({
      model: "tts-1",
      voice: voice,
      input: userInput,
    });
    const buffer = Buffer.from(await mp3.arrayBuffer());
    await fs.promises.writeFile(uniqueFileName, buffer);
  } catch (error) {
    console.error("Error in chat method:", error);
    throw error;
  }
}

async function connectToDb() {
  try {
    await client.connect();
    // await client.db("admin").command({ ping: 1 });
    // console.log("Pinged your deployment. You successfully connected to MongoDB!");

    db = client.db("remibot");
    conversationsCollection = db.collection("conversations");
  } catch (error) {
    console.error("Failed to connect to MongoDB:", error);
  }
}

async function createConversation(userName) {
  try {
    await connectToDb();
    const conversation = await conversationsCollection.findOne({
      user_name: userName,
    });
    if (!conversation) {
      const newConversation = {
        user_name: userName,
        voice: VOICE_CHOICE[Math.floor(Math.random() * VOICE_CHOICE.length)],
        messages: [],
      };
      await conversationsCollection.insertOne(newConversation);
    }
  } catch (error) {
    console.error("An error occurred:", error);
  } finally {
    await client.close();
  }
}

async function findOthers(selfUsername) {
  try {
    await connectToDb();
    const allUsernames = await conversationsCollection.distinct("user_name");
    const otherUsernames = allUsernames.filter((user) => user !== selfUsername);
    return otherUsernames;
  } catch (error) {
    console.error("Failed to find other usernames:", error);
    return [];
  } finally {
    await client.close();
  }
}

async function addMessage(userName, message) {
  try {
    await connectToDb();

    const messageWithTimestamp = {
      text: message,
      timestamp: new Date(),
    };

    await conversationsCollection.updateOne(
      { user_name: userName },
      { $push: { messages: messageWithTimestamp } },
      { upsert: true }
      // { $push: { messages: message } }
    );
    console.log("Message added successfully");
  } catch (error) {
    console.error("Failed to add message:", error);
  } finally {
    await client.close();
  }
}

function weightedChoice(items, weights) {
  if (items.length !== weights.length) {
    throw new Error("Items and weights must be of the same length");
  }

  const totalWeight = weights.reduce((acc, weight) => acc + weight, 0);
  let pick = Math.random() * totalWeight;

  for (let i = 0; i < items.length; i++) {
    pick -= weights[i];
    if (pick < 0) {
      return items[i];
    }
  }
  throw new Error("Failed to pick an item based on the given weights");
}

const bot = new HallucinatedChatbot();

export async function initChat(userName) {
  await createConversation(userName);
  bot.username = userName;
  const others = await findOthers(bot.username, bot.conversations);
  bot.random_user = others[Math.floor(Math.random() * others.length)];

  console.log(`${bot.username}, ${bot.random_user}`);
}

export async function chat(userName, message, uniqueFileName) {
  await addMessage(userName, message);
  const response = await bot.chat(message, uniqueFileName);
  return response;
}

// async function addTimestampsToMessages() {
//   try {
//     await connectToDb();
//     const users = await conversationsCollection.find({}).toArray();

//     for (let user of users) {
//       const updatedMessages = user.messages.map(message => {
//         if (typeof message === 'string') {
//           return {
//             text: message,
//             timestamp: new Date(),
//           };
//         }
//         return message;
//       });

//       await conversationsCollection.updateOne(
//         { _id: user._id },
//         { $set: { messages: updatedMessages } }
//       );
//     }

//     console.log("All messages updated with timestamps successfully");
//   } catch (error) {
//     console.error("Failed to update messages with timestamps:", error);
//   } finally {
//     await client.close();
//   }
// }

// addTimestampsToMessages().catch(console.error);
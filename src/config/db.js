require('dotenv').config();

const { MongoClient, ServerApiVersion } = require('mongodb');
const uri = process.env.MONGO_URI;

const client = new MongoClient(uri, {
    serverApi: {
        version: ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
    }
});

const connectToDatabase = async () => {
    try {
        await client.connect();

        await client.db("Brands").command({ ping: 1 });
        console.log(client);
        console.log("pinged deployment, successfully connected to mongo db");
    } finally {
        await client.close();
    }
}

connectToDatabase().catch(console.dir);

module.exports = connectToDatabase;
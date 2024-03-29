import express from 'express';
import cors from 'cors';
import { v4 as uuidv4 } from 'uuid';
import { initChat, chat } from './conversation.js';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const app = express();
const __dirname = path.dirname(fileURLToPath(import.meta.url));

let name;

app.use(cors());
app.use(express.json());

app.post('/init_chat', (req, res) => {
    name = req.body.name;
    initChat(name);
    res.json({ message: `Hello ${name}, Let's chat!` });
});

app.post('/send_text', async (req, res) => {
    const text = req.body.text;
    const uniqueFilename = `response_${uuidv4()}.mp3`;

    try {
        const responseText = await chat(name, text, uniqueFilename);
        const audioUrl = `${req.protocol}://${req.get('host')}/audio/${uniqueFilename}`;
        res.json({ response_text: responseText, mp3_url: audioUrl });
    } catch (error) {
        console.error('Error during chat processing:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/audio/:filename', (req, res) => {
    const filename = req.params.filename;
    const filePath = path.join(__dirname, filename);

    fs.access(filePath, fs.constants.F_OK, (err) => {
        if (err) {
            console.error('File not found:', filename);
            return res.status(404).json({ error: 'File not found' });
        }
        res.sendFile(filePath);
    });
});

app.post('/audio_played', (req, res) => {
    const { filename } = req.body;
    const filePath = path.join(__dirname, filename);
    fs.unlink(filePath, (err) => {
        if (err) {
            console.error('Error deleting the file:', err);
            return res.status(500).json({ error: 'Failed to delete the file' });
        }
        res.json({ message: 'File deleted successfully' });
    });
});

const port = process.env.PORT || 2024;
app.listen(port, () => console.log(`Server running on port ${port}`));

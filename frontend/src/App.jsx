import React, { useState } from 'react';
import axios from 'axios';
import { Send, User, Bot, History } from 'lucide-react';

function App() {
  const [messages, setMessages] = useState([
    { text: "Hello! Hospital Bot-ku welcome. Unga Patient ID iruntha sollunga, illena unga issue-ah type pannunga.", sender: "bot" }
  ]);
  const [input, setInput] = useState("");
  const [patientId, setPatientId] = useState("");

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // 1. User message-ah screen-la instant-ah update panrom
    const userMsgObj = { text: input, sender: "user" };
    setMessages(prev => [...prev, userMsgObj]);
    
    const currentUserInput = input;
    setInput("");

    try {
      // ✅ Updated Axios Call: Sending data as Query Params to match your FastAPI @app.post setup
      const response = await axios.post("https://hospital-backend-1l0j.onrender.com/chat", null, {
        params: {
          user_msg: currentUserInput,
          p_id: patientId || ""
        }
      });

      // 3. Bot-oda reply-ah screen-la kaatuvom
      if (response.data && response.data.reply) {
        setMessages(prev => [...prev, { text: response.data.reply, sender: "bot" }]);
      }
    } catch (error) {
      console.error("Error connecting to backend:", error);
      
      let errorMsg = "Backend kooda connect panna mudiyala. ";
      if (error.response) {
        errorMsg += `Server Error: ${error.response.status}`;
      } else {
        errorMsg += "Check your internet or Render backend status.";
      }

      setMessages(prev => [...prev, { text: errorMsg, sender: "bot" }]);
    }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Bot size={28} />
          <h2 style={{ margin: 0 }}>Hospital Assistant</h2>
        </div>
        <div style={styles.patientBox}>
          <History size={18} />
          <input 
            placeholder="Patient ID" 
            value={patientId} 
            onChange={(e) => setPatientId(e.target.value)}
            style={styles.idInput}
          />
        </div>
      </header>

      <div style={styles.chatWindow}>
        {messages.map((msg, index) => (
          <div key={index} style={msg.sender === 'user' ? styles.userMsgWrapper : styles.botMsgWrapper}>
            <div style={msg.sender === 'user' ? styles.userMsg : styles.botMsg}>
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage} style={styles.inputArea}>
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="Type your symptoms here..."
          style={styles.mainInput}
        />
        <button type="submit" style={styles.sendBtn}><Send size={20} /></button>
      </form>
    </div>
  );
}

const styles = {
  container: { maxWidth: '600px', margin: '20px auto', fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', border: '1px solid #ddd', borderRadius: '15px', display: 'flex', flexDirection: 'column', height: '85vh', boxShadow: '0 4px 15px rgba(0,0,0,0.1)', background: '#fff' },
  header: { background: '#2c3e50', color: 'white', padding: '15px 20px', borderRadius: '15px 15px 0 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  patientBox: { display: 'flex', alignItems: 'center', background: '#34495e', padding: '5px 12px', borderRadius: '20px' },
  idInput: { background: 'transparent', border: 'none', color: 'white', marginLeft: '5px', outline: 'none', width: '90px', fontSize: '14px' },
  chatWindow: { flex: 1, padding: '20px', overflowY: 'auto', background: '#f4f7f6', display: 'flex', flexDirection: 'column' },
  userMsgWrapper: { alignSelf: 'flex-end', marginBottom: '10px', display: 'flex', justifyContent: 'flex-end', width: '100%' },
  botMsgWrapper: { alignSelf: 'flex-start', marginBottom: '10px', display: 'flex', justifyContent: 'flex-start', width: '100%' },
  userMsg: { background: '#3498db', color: 'white', padding: '12px 16px', borderRadius: '15px 15px 0 15px', maxWidth: '85%', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' },
  botMsg: { background: '#fff', color: '#2c3e50', padding: '12px 16px', borderRadius: '15px 15px 15px 0', maxWidth: '85%', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', border: '1px solid #eee' },
  inputArea: { display: 'flex', padding: '15px', borderTop: '1px solid #eee', background: '#fff', borderRadius: '0 0 15px 15px' },
  mainInput: { flex: 1, padding: '12px', borderRadius: '25px', border: '1px solid #ddd', outline: 'none', fontSize: '15px' },
  sendBtn: { background: '#27ae60', color: 'white', border: 'none', width: '45px', height: '45px', marginLeft: '10px', borderRadius: '50%', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: '0.3s' }
};

export default App;
import { useState,useEffect,useRef } from 'react'
import './App.css'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [socket, setSocket] = useState(null)
  const [port, setPort] = useState(8000)

  useEffect(() => {

    const websocket = new WebSocket(`ws://localhost:${port}/`)
    setSocket(websocket)

    return () => {
      websocket.close()
    }
  }, [port]
  )

  function onInputChange(e){
    setInput(e.target.value)
  }

  function sendMessage(e){
    e.preventDefault()
    if (input){
      socket.send(input)
      setMessages(prevMessages=>
      [...prevMessages,{'text':input,type:'sent'}])
      setInput('')
    }
  }

  useEffect(()=>{
    if(socket){
      socket.onmessage = (event)=>{
          const {data} = event
          setMessages(prevMessages=>
            [...prevMessages,{'text':data,type:'received'}])
      }
    }
  },[socket])

  return (
    <div>
    <div className='select-server'>
      <form>
        <label>Run on:</label>
        <select onChange={(event)=>{setPort(event.target.value)}}>
          <option value = "8080">Port 8080</option>
          <option value = "8000">Port 8000</option>
        </select>
      </form>

    </div>
        <div className='message-container'>
          {
            messages.map((message,i)=>(
              <div key={i} className={`${message.type == 'sent'?'sent-message':'received-message'}`}>{message.text}</div>
            ))
          }
        </div>
        <form className='chat-form' onSubmit={sendMessage}>
          <input type='text' placeholder='send message' value={input} onChange={onInputChange}/>
          <button type='submit'>Send</button>
        </form>
    </div>
  )
}

export default App

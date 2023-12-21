import {  useEffect, useState } from "react";
import { 
  Button, 
  Typography, 
  Image, 
  Upload, 
  Progress, 
  Space 
} from "antd";


export default function CameraPage() {
  const [image, setImage] = useState<any>(null)

  useEffect(()=>{
    let es = new EventSource(`${process.env.API_ADDR}/camera`)
    es.onerror = e=>{
      es.close()
    }
    es.onmessage = (e)=>{
      const data = JSON.parse(e.data)
      if(data.type === 'image'){
        setImage(data.image)
      }else if(data.type==='error'){
        es.close()
      }
    }
    es.onopen = e=>console.log(e)

  },[])

  return (
    <Space direction="vertical" align="center" size='small'>
      <Typography.Title>recognize face via camera</Typography.Title>
      <div style={{ width: 640, height: 360, display: 'flex', flexDirection:'column', justifyContent:'center', alignItems:'center' }}>
        <Image src={image} width='100%' height={360} preview={false}/>
      </div>
    </Space>
  )
}
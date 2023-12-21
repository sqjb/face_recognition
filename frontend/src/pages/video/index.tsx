import {  useEffect, useState } from "react";
import { 
  Button, 
  Typography, 
  Image, 
  Upload, 
  Progress, 
  Space 
} from "antd";


export default function VideoPage() {
  const [image, setImage] = useState<any>(null)
  const [text, setText] = useState<string>('upload')

  // upload button
  const [disabled, setDisabled] = useState<boolean>(false)

  // progress
  const [percent, setPercent] = useState(0)
  const twoColors = { '0%': '#108ee9', '100%': '#87d068' };

  // SSE request
  const fetchvideo = (url:string)=>{
    let es = new EventSource(url)
    es.onerror = e=>{
      es.close()
      setDisabled(false)
      setText('upload')
    }
    es.onmessage = (e)=>{
      const data = JSON.parse(e.data)
      if(data.type === 'image'){
        setImage(data.image)
      }else if(data.type==='error'){
        es.close()
        setDisabled(false)
        setText('upload')
      }
    }
    es.onopen = e=>console.log(e)
  }

  return (
    <Space direction="vertical" align="center" size='small'>
      <Typography.Title>upload an video file for face recognition</Typography.Title>
      <div style={{ width: 640, height: 360, display: 'flex', flexDirection:'column', justifyContent:'center', alignItems:'center' }}>
        <Image src={image} width='100%' height={360} preview={false}/>
      </div>
      <div>
          <Upload
            accept=".mp4,.flv,.avi"
            action={`${process.env.API_ADDR}/video/upload`}
            name="file"
            showUploadList={false}
            onChange={info=>{
              if(info.event){
                setPercent(info.event.percent)
              }
              // text
              const status = info.file.status
              if(status) {
                if(status==='done'){
                  const resp = info.file.response
                  if(resp.result === true) {
                    setText('playing')
                    // request event-stream
                    let url = `${process.env.API_ADDR}/video?file=${resp.data}`
                    setDisabled(true)
                    fetchvideo(url)
                  }else{
                    setText('err:' + resp.message)
                  }
                } else {
                  setText(status)
                }
              }

              
            }}
            
          >
            <Button size="small" style={{ width: 100 }} disabled={disabled}>{text}</Button>
            <Progress 
              style={{ margin:0 }}
              percent={percent} 
              strokeColor={twoColors} 
              showInfo={false} 
              strokeWidth={2}/>
          </Upload>
        </div>

    </Space>
  )
}
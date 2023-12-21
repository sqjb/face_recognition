import person from '../../assets/person.png'
import { PlusOutlined } from '@ant-design/icons'
import ReactJson from 'react-json-view'
import {
  Button,
  Card,
  Divider,
  Flex,
  Image,
  Select,
  Space,
  Typography, Upload
} from 'antd'
import { useState } from 'react'
import './image.less'
import { RcFile } from 'antd/es/upload'
import { noop } from 'antd/es/_util/warning'
const UploadButton = () => (<div>
  <PlusOutlined />
  <div style={{ marginTop: 8 }}>Upload</div>
</div>)

export default function ImagePage() {
  const [file, setFile] = useState<any>(null)
  const [imgUrl, setImgUrl] = useState<any>(null)
  const [result, setResult] = useState<any>(null)
  const handleFileUpload = (file: RcFile) => {
    const formdata = new FormData()
    formdata.append("image", file)
    setImgUrl(null)
    setResult(null)
    fetch(`${process.env.API_ADDR}/image`, {
      method: 'POST',
      body: formdata
    })
      .then(res => res.json())
      .then(ret => {
        console.log(ret)
        setResult(ret)
        if (ret.result === true) {
          setImgUrl(`${process.env.API_ADDR}/${ret.data.path}`)
        }
        return
      })
  }
  return (<div>
    <Typography.Title> upload your image with face </Typography.Title>
    <Space style={{ textAlign: 'left' }}>
      <Card bodyStyle={{ padding: 8 }}>
        <Space>
          <Space direction='vertical' align='center'>
            <div className='m-image-wrapper'>
              <Image
                src={file}
                //fallback={facebg} 
                preview={false}
                style={{ maxWidth: '100%', maxHeight: '100%' }}

              />
            </div>
            <Upload
              accept=".png,.jpeg,.jpg"
              showUploadList={false}
              beforeUpload={(file: RcFile) => {
                const reader = new FileReader()
                reader.readAsDataURL(file)
                reader.onload = e => {
                  setFile(e.target?.result)
                }
                handleFileUpload(file)
                return false
              }}
            >
              <Button size='small' type='dashed' block >click to upload</Button>
            </Upload>
          </Space>
          <Space direction='vertical' align='center'>
            <div className='m-image-wrapper1'>
              <Image src={imgUrl} fallback={person} style={{ maxWidth: '100%', maxHeight: '100%', height: 300 }} />
            </div>
            <Typography.Text >
              {result && result.result ? result.data.name : 'name?'}
            </Typography.Text>
          </Space>
        </Space>
      </Card>
      <Card
        title='JSON Response'
        size='small'
        bodyStyle={{ height: 310, width: 500 }}
      >
        <div className='m-json-view-wrapper'>
          {result ? <ReactJson src={result} name={false} displayDataTypes={false} /> : null}
        </div>
      </Card>
    </Space>
  </div>)
}
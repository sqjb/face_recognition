import { Avatar, Table, message } from 'antd'
import { useEffect, useState } from 'react'
const columns = [
  { key:'id', dataIndex: 'id', title:'ID' },
  { key:'name', dataIndex: 'name', title:'name' },
  { key:'image', dataIndex: 'image', title:'image', render: (path:any)=><Avatar src={path} size={48}/> },
  { key:'registered_at', dataIndex: 'registered_at', title:'registered at', render: (d:any)=>new Date(d*1000).toLocaleString() },
]

export default function FaceListPage(){
  const [messageApi, contextHolder] = message.useMessage();
  const [faces, setFaces] = useState<any>([])
  const [total, setTotal] = useState<number>(0)

  const getfaces = async ()=>{
    try {
      const response = await fetch(`${process.env.API_ADDR}/faces`)
      const data = await response.json()
      const fs = []
      for(var i=0;i<data.data.length;i++) {
        fs.push({
          key: i,
          id: i,
          name: data.data[i].name,
          image: `${process.env.API_ADDR}/${data.data[i].path}`,
          registered_at: data.data[i].registered_at,
        })
      }
      setFaces([...fs])
      setTotal(data.total)
    }catch(err) {
      messageApi.error(String(err))
    }
  }

  useEffect(()=>{
    getfaces()
  },[])

  return (<div style={{ width:'60%' }}>
    {contextHolder}
    <Table 
      columns={columns} 
      dataSource={faces} 
      scroll={{ x:'max-content', y:500}} 
      size='small'/>
  </div>)
}
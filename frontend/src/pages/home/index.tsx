import faceJpg from '../../assets/face.png';
import {
  Button,
  Space,
  Typography
} from 'antd';
import './home.less'
import { Link } from 'umi';

const { Text, Title } = Typography;
export default function HomePage() {
  return (
    <div>
      <Title>a simple face recognition app</Title>
      <Text type='secondary' style={{ textTransform: 'uppercase' }} >
        react、python、dlib、flask、opencv
      </Text>
      <p>
        <img src={faceJpg} width="388" />
      </p>

      <Space>
        <Link to='/faces'>
          <Button className='button-color-volcano'>faces</Button>
        </Link>
        <Link to='/image'>
          <Button className='button-color-sunset'>image</Button>
        </Link>
        <Link to='/video'>
          <Button className='button-color-green'>video</Button>
        </Link>
        <Link to='/camera'>
        <Button className='button-color-daybreak'>camera</Button>
        </Link>
        
      </Space>
    </div>
  );
}

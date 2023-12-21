import { Link, Outlet } from 'umi';
import styles from './index.less';
import { Space } from 'antd';

export default function Layout() {
  return (
    <div className={styles.main}>
      <Outlet />
      <div>
        <Space>
          <Link to='/'>HOME</Link>
          <a href='https://github.com/sqjb/face_recoginiton'>GITHUB</a>
        </Space>
      </div>
    </div>
  );
}
